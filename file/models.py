from hashlib import sha3_512
from django.db import models

# Create your models here.
class File(models.Model):
    fid = models.UUIDField()
    filename = models.TextField()
    keyhash = models.TextField()
    expires_at = models.DateTimeField(null=True)
    def __init__(self):
        super(File, self).__init__()
    @property
    def is_avail(self):
        return self.check_file()
    def check_file(self):
        pass
    def iter_decrypt_read(self, aes_key: bytes):
        pass
    def iter_write(self):
        pass