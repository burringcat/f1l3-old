import mimetypes
import os
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseBadRequest, JsonResponse, StreamingHttpResponse
from django.shortcuts import render

from utils.utils import AESCrypto
from file.models import File


def handle_uploaded_file(f):
    fpath = os.path.join(settings.MEDIA_ROOT, f.fid)
    with open(fpath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    kh = AESCrypto.key_hash(f.encryptor.key)
    k = f.encryptor.key_str
    file_obj = File.objects.create(fid=f.fid, filename=f.file_name,
                        keyhash=kh,
                        expires_at=File.expire_time(f.encrypted_file_size),
                        file_path=fpath, real_size_bytes=f.real_size, aes_iv=f.iv)
    return f'http://{settings.HOST}/d/{f.fid}/k/{k}/{f.file_name}', file_obj.expires_at


def main_on_post(request):
    file = request.FILES.get('file')
    if file is not None:
        url, expires_at = handle_uploaded_file(file)
        expires_at = str(expires_at) if expires_at else None
        return JsonResponse({'message': 'OK', 'is_uploaded': True,
                             'url': url, 'status': 200, 'expires_at': expires_at})
    return JsonResponse({'message': 'Bad request', 'is_uploaded': False,
                         'url': None, 'status': 400, 'expires_at': None})


def main_on_get(request):
    return render(request, 'f1l3/index.html')


def main(request):
    if request.method == 'GET':
        return main_on_get(request)
    if request.method == 'POST':
        return main_on_post(request)


def download(request, fid, key, filename):
    bytes_key = AESCrypto.str2key(key)
    kh = AESCrypto.key_hash(bytes_key)
    file = File.objects.filter(fid=fid, keyhash=kh).first()
    if file is None or not File.is_avail(file):
        return HttpResponseNotFound()
    content_type = mimetypes.guess_type(filename)[0]
    resp = StreamingHttpResponse(file.iter_decrypt_read(bytes_key),
                                 status=200, content_type=content_type)
    # resp['Content-Disposition'] = 'attachment; filename=' + file.filename
    return resp


def handle500(request):
    return JsonResponse({'message': 'File too large or there is a server error', 'status': 500})
