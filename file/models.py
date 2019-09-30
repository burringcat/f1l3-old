from datetime import timedelta, datetime
from django.db import models
from django.utils import timezone
from django.conf import settings

from utils.utils import AESCrypto


# Create your models here.
class File(models.Model):
    fid = models.TextField()
    filename = models.TextField()
    keyhash = models.TextField()
    expires_at = models.DateTimeField(null=True)
    file_path = models.FilePathField(null=True)
    real_size_bytes = models.BigIntegerField(default=0)
    aes_iv = models.BinaryField(default=b'')

    @staticmethod
    def expire_time(file_size):
        if file_size > settings.F1L3_FILE_SIZE_LIMIT:
            return timezone.now()
        hours = 0
        for s, t in sorted(settings.F1L3_FILE_EXPIRATION_SETTINGS.items(), key=lambda x: x[0]):
            if file_size < s:
                hours = t
                break
        if hours >= 0:
            return timezone.now() + timedelta(hours=hours)
        else:
            return None

    @staticmethod
    def is_avail(file_obj):
        is_avail = file_obj.check_expiration()
        if is_avail is False:
            file_obj.delete()
        return is_avail

    def check_expiration(self):
        return self.expires_at is None or timezone.now() < self.expires_at

    def iter_decrypt_read(self, aes_key: bytes):
        aes_crypto = AESCrypto(key=aes_key)
        return aes_crypto.iter_decrypt_file(self.file_path,
                                            ivnsz=(self.aes_iv, self.real_size_bytes))
