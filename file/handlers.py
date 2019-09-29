from django.core.files.uploadhandler import TemporaryFileUploadHandler, StopUpload
from django.conf import settings
from utils.utils import AESCrypto
class EncryptedTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        if content_length > settings.F1L3_FILE_SIZE_LIMIT:
            raise StopUpload(connection_reset=True)

    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.file.encrypted_file_size = 0
        self.file.real_size = 0
        self.file.encryptor = AESCrypto()

    def receive_data_chunk(self, raw_data, start):
        self.file.real_size += len(raw_data)
        rdata_len_mod = len(raw_data) % 16
        if rdata_len_mod != 0:
            raw_data += bytes(' ' * (16 - rdata_len_mod), encoding='utf8')
        edata = self.file.encryptor.encrypt(raw_data)
        self.file.write(edata)
        self.file.encrypted_file_size += len(edata)

    def file_complete(self, file_size):
        print(self.file.encrypted_file_size)
        header = self.file.encryptor.file_header_data(self.file.real_size)
        self.file.write(header)
        self.file.encrypted_file_size += len(header)
        self.file.seek(0)
        self.file.size = int(self.file.encrypted_file_size)
        del self.file.encrypted_file_size
        return self.file
