import mimetypes
from django.http import HttpResponse, HttpResponseNotFound

from utils.utils import AESCrypto

from file.models import File
# Create your views here.
def main_on_post(request):
    pass
def main_on_get(request):
    pass
def main(request):
    if request.method == 'GET':
        return main_on_get(request)
    if request.method == 'POST':
        return main_on_post(request)

def download(request, fid, key):
    bytes_key = AESCrypto.str2key(key)
    kh = AESCrypto.key_hash(bytes_key)
    file = File.objects.filter(fid=fid, keyhash=kh).first()
    if file is None or not file.is_avail:
        return HttpResponseNotFound()
    content_type = mimetypes.guess_type(file.filename)
    resp = HttpResponse(file.iter_decrypt_read(), status=200, content_type=content_type)
    resp['Content-Disposition'] = 'attachment; filename=' + file.filename
    return resp