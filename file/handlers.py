from django.core.files.uploadhandler import TemporaryFileUploadHandler
from utils.utils import AESCrypto
class EncryptedTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.file.encrypted_file_size = 0
        self.file.encryptor = AESCrypto()

    def receive_data_chunk(self, raw_data, start):
        if self.file.encrypted_file_size == 0:
            fsz = self.file.size
            header = self.file.encryptor.file_header_data(fsz)
            self.file.write(header)
            self.file.encrypted_file_size += len(header)
        rdata_len_mod = len(raw_data) % 16
        if rdata_len_mod != 0:
            raw_data += bytes(' ' * (16 - rdata_len_mod), encoding='utf8')
        edata = self.file.encryptor.encrypt(raw_data)
        self.file.write(edata)
        self.file.encrypted_file_size += len(edata)

    def file_complete(self, file_size):
        self.file.seek(0)
        self.file.size = self.file.encrypted_file_size
        del self.file.encrypted_file_size
        return self.file
