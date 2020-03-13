from datetime import timedelta
import os

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_delete, pre_migrate, pre_save
from django.dispatch import receiver

from utils.utils.crypto import AESCrypto

# Create your models here.
class File(models.Model):
    fid = models.TextField(primary_key=True)
    filename = models.TextField()
    keyhash = models.TextField()
    expires_at = models.DateTimeField(null=True)
    file_path = models.FilePathField(null=True)
    real_size_bytes = models.BigIntegerField(default=0)
    aes_iv = models.BinaryField(default=b'')
    @classmethod
    def clear_expired(cls):
        expired = cls.objects.\
            filter(expires_at__isnull=False).\
            filter(expires_at__lt=timezone.now()).\
            all()
        expired_fids = (f.fid for f in expired)
        expired.delete()
        return expired_fids
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
        return file_obj.fid not in File.clear_expired()

    def check_expiration(self):
        return self.expires_at is None or timezone.now() < self.expires_at

    def iter_decrypt_read(self, aes_key: bytes):
        aes_crypto = AESCrypto(key=aes_key)
        return aes_crypto.iter_decrypt_file(self.file_path,
                                            ivnsz=(self.aes_iv, self.real_size_bytes))


def clear_expired_hook(sender, instance: File, using, **kwargs):
    File.clear_expired()
for signal in (pre_save, pre_migrate):
    receiver(signal, sender=File)(clear_expired_hook)


@receiver(post_delete, sender=File)
def delete_actual_file(sender, instance: File, using, **kwargs):
    if os.path.isfile(instance.file_path):
        os.remove(instance.file_path)
