from base64 import b64encode
from hashlib import sha3_256
from django.db import models
from django.contrib.auth.models import User
from Crypto.Random import get_random_bytes
# Create your models here.
class IPAddress(models.Model):
    address_hash = models.TextField()
    def __init__(self, address: str):
        address_hash = sha3_256(address.encode()).hexdigest()
        super(IPAddress, self).__init__(address_hash=address_hash)



class F1L3User(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token_hash = models.TextField(null=True)
    ip = models.ForeignKey(IPAddress, on_delete=models.SET_NULL)
    def __init__(self, *args, **kwargs):
        super(F1L3User, self).__init__(*args, **kwargs)

    @classmethod
    def generate_token_hash(cls, token: str):
        return sha3_256(token.encode()).hexdigest()
    @classmethod
    def generate_token(cls):
        rbytes = get_random_bytes(128)
        token = str(b64encode(rbytes), encoding='utf8')
        return token
    @classmethod
    def auth_by_token(cls, token):
        if not token:
            return None
        token_hash = cls.generate_token_hash(token)
        return F1L3User.objects.filter(token_hash=token_hash).first()
