from uuid import uuid4
from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.conf import settings
from utils.utils import AESCrypto

class EncryptedUploadedFile(TemporaryUploadedFile):
    def __init__(self, *args, **kwargs):
        super(EncryptedUploadedFile, self).__init__(*args, **kwargs)
        self.file_name = None
        self.encrypted_file_size = 0
        self.real_size = 0
        self.encryptor = AESCrypto()
        self.iv = AESCrypto.gen_iv()
        self.aes = self.encryptor.aes(self.iv)
        self.fid = None

class EncryptedTemporaryFileUploadHandler(FileUploadHandler):
    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        if content_length > settings.F1L3_FILE_SIZE_LIMIT:
            raise StopUpload(connection_reset=True)

    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        fid = str(uuid4())
        self.file = EncryptedUploadedFile(fid,
                                          self.content_type, 0, self.charset, self.content_type_extra)
        self.file.file_name = self.file_name
        self.file.fid = fid
    def receive_data_chunk(self, raw_data, start):
        self.file.real_size += len(raw_data)
        rdata_len_mod = len(raw_data) % 16
        if rdata_len_mod != 0:
            raw_data += bytes(' ' * (16 - rdata_len_mod), encoding='ascii')
        edata = self.file.aes.encrypt(raw_data)
        self.file.write(edata)
        self.file.encrypted_file_size += len(edata)

    def file_complete(self, file_size):
        self.file.seek(0)
        self.file.size = int(self.file.encrypted_file_size)
        del self.file.aes
        return self.file
