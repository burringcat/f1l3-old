from os import SEEK_END
from hashlib import sha3_512
import struct
from base64 import b16decode, b16encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from django.core.files.base import File
from django.conf import settings


def secret_key_aes():
    k = settings.SECRET_KEY
    if len(k) < 32:
        k = k.ljust(32, ' ')
    return AES.new(bytes(k, encoding='utf8')[:16],
                   AES.MODE_CBC, bytes(k, encoding='utf8')[16:32])


class AESCrypto:
    _header_size = struct.calcsize('<Q') + 16

    def __init__(self, key=None):
        self.key = key or self.gen_key(32)
        if isinstance(self.key, str):
            self.key = self.str2key(self.key)

    @staticmethod
    def gen_iv() -> bytes:
        return get_random_bytes(16)

    @staticmethod
    def gen_key(keylen):
        return get_random_bytes(keylen)

    @staticmethod
    def key2str(key) -> str:
        s = secret_key_aes().encrypt(key)
        s = str(b16encode(s), encoding='utf-8')
        return s

    @staticmethod
    def str2key(s) -> bytes:
        s = s.upper()
        key = b16decode(bytes(s, encoding='utf-8'))
        key = secret_key_aes().decrypt(key)
        return key

    @staticmethod
    def key_hash(k: bytes):
        kh = sha3_512(k).hexdigest()
        return kh

    def aes(self, iv: bytes):
        return AES.new(self.key, AES.MODE_CBC, iv)

    def file_header_data(self, file_size, iv):
        return struct.pack('<Q', file_size) + iv

    def iter_encrypt_file(self, file, file_size: int = 0, chunk_size=File.DEFAULT_CHUNK_SIZE, reverse_header_pos=True):
        def calc_file_size():
            file.seek(0, SEEK_END)
            sz = file.tell()
            file.seek(0)
            return sz

        file_size = file_size if file_size != 0 else calc_file_size()
        iv = self.gen_iv()
        header = self.file_header_data(file_size, iv)
        if reverse_header_pos is False:
            yield header
        mod = chunk_size % 16
        if mod != 0:
            chunk_size += 16 - mod
        while True:
            data = file.read(chunk_size)
            read_size = len(data)
            rdmod = read_size % 16
            if read_size == 0:
                break
            elif rdmod != 0:
                data += bytes(' ' * (16 - rdmod), encoding='ascii')
            encrypted_data = self.aes(iv).encrypt(data)
            yield encrypted_data
        if reverse_header_pos:
            yield header

    def iter_decrypt_file(self, encrypted_file_path: str, chunk_size=File.DEFAULT_CHUNK_SIZE
                          , reverse_header_pos=True, *args, ivnsz: tuple = None):
        encrypted_file = open(encrypted_file_path, 'rb')
        if ivnsz is None:
            if reverse_header_pos:
                encrypted_file.seek(0, SEEK_END)
                encrypted_file_size = encrypted_file.tell()
                encrypted_file.seek(-self._header_size, SEEK_END)

            remaining_file_size = struct.unpack('<Q',
                                                encrypted_file.read(
                                                    struct.calcsize('<Q')))[0]
            iv = encrypted_file.read(16)

            if reverse_header_pos:
                encrypted_file.seek(0)
        else:
            remaining_file_size = ivnsz[1]
            iv = ivnsz[0]
        aes = self.aes(iv)

        while True:
            data = encrypted_file.read(chunk_size)
            read_size = len(data)
            if read_size == 0:
                break
            if ivnsz is None and reverse_header_pos and \
                    encrypted_file.tell() == encrypted_file_size:
                data = data[:len(data) - self._header_size]
            ori_data = aes.decrypt(data)
            ori_data_size = len(ori_data)
            if remaining_file_size > ori_data_size:
                yield ori_data
            else:
                # remove padding spaces
                yield ori_data[:remaining_file_size]
            remaining_file_size -= ori_data_size
        encrypted_file.close()

    @property
    def key_str(self):
        return self.key2str(self.key)
