from os import SEEK_END, SEEK_SET
from hashlib import sha3_512
import struct
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b32decode, b32encode
class AESCrypto:
    def __init__(self, key=None):
        self.key = key or self.gen_key(16)
        if isinstance(self.key, str):
            self.key = self.str2key(self.key)
        self.iv = None
        self._aes = None

    @staticmethod
    def _gen_iv() -> bytes:
        return get_random_bytes(16)
    @staticmethod
    def gen_key(keylen):
        return get_random_bytes(keylen)
    @staticmethod
    def key2str(key) -> str:
        s = str(b32encode(key), encoding='utf-8')
        return s
    @staticmethod
    def str2key(s) -> bytes:
        key = b32decode(bytes(s))
        return key
    @staticmethod
    def key_hash(k: bytes):
        kh = sha3_512(k).hexdigest()
        return kh

    def encrypt(self, data: bytes) -> bytes:
        return self.aes.encrypt(data)
    def decrypt(self, data:bytes) -> bytes:
        return self.aes.decrypt(data)

    def iter_encrypt_file(self, file, chunk_size=1024*16):
        file.seek(0, SEEK_END)
        file_size = file.tell()
        file.seek(SEEK_SET)
        yield struct.pack('<Q', file_size)
        yield self.iv
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
                data += ' ' * (16 - rdmod)
            encrypted_data = self.encrypt(data)
            yield encrypted_data

    def iter_decrypt_file(self, encrypted_file, chunk_size=1024*16):
        remaining_file_size = struct.unpack('<Q',
                                  encrypted_file.read(
                                      struct.calcsize('<Q')))[0]
        self.iv = encrypted_file.read(16)
        while True:
            data = encrypted_file.read(chunk_size)
            read_size = len(data)
            if read_size == 0:
                break
            ori_data = self.decrypt(data)
            ori_data_size = len(ori_data)
            if remaining_file_size > ori_data_size:
                yield ori_data
            else:
                # remove padding spaces
                yield ori_data[:remaining_file_size]
            remaining_file_size -= ori_data_size


    @property
    def key_str(self):
        return self.key2str(self.key)

    @property
    def aes(self):
        if self.iv is None:
            self.iv = self._gen_iv()
        if self._aes is None:
            self._aes = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self._aes