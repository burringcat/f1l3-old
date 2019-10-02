import mimetypes
import os
import binascii
from django.conf import settings
from django.http import HttpResponseNotFound, JsonResponse, StreamingHttpResponse, \
    HttpResponse
from django.shortcuts import render

from utils.utils.crypto import AESCrypto
from utils.utils.setting_utils import readable_size_rules
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
    url = f'/{k.lower()}{os.path.splitext(f.file_name)[1]}'
    if settings.HOST:
        url = f'https://{settings.HOST}{url}'
    return url, file_obj.expires_at


def upload_response(url: str = None, expires_at: str = None, json_response=False):
    if json_response:
        if url:
            return JsonResponse({'message': 'OK', 'is_uploaded': True,
                                 'url': url, 'status': 200, 'expires_at': expires_at})
        else:
            return JsonResponse({'message': 'Bad request', 'is_uploaded': False,
                                 'url': None, 'status': 400, 'expires_at': None})
    else:
        return HttpResponse(url if url else '400')


def upload(request):
    file = request.FILES.get('file')
    json_response = request.GET.get('json', request.POST.get('json'))
    json_response = True if json_response else False
    if file is not None:
        url, expires_at = handle_uploaded_file(file)
        expires_at = str(expires_at) if expires_at else None
        return upload_response(url, expires_at, json_response)
    return upload_response(json_response=json_response)


def main(request):
    host = settings.HOST if settings.HOST else 'host'
    max_size_mb = settings.F1L3_FILE_SIZE_LIMIT / settings.MB
    context = {'host': host, 'size_rules': readable_size_rules(), 'max_size_mb': max_size_mb}
    return render(request, 'f1l3/index.html', context=context)


def handle_key(key, content_type_url):
    try:
        bytes_key = AESCrypto.str2key(key)
    except binascii.Error:
        return HttpResponseNotFound()
    kh = AESCrypto.key_hash(bytes_key)
    file = File.objects.filter(keyhash=kh).first()
    if file is None or not File.is_avail(file):
        return HttpResponseNotFound()
    content_type = mimetypes.guess_type(content_type_url)[0]
    resp = StreamingHttpResponse(file.iter_decrypt_read(bytes_key),
                                 status=200, content_type=content_type)
    # resp['Content-Disposition'] = 'attachment; filename=' + file.filename
    return resp


def download(request, key, ext):
    return handle_key(key, 'filename.' + ext)


def download_no_ext(request, key):
    return handle_key(key, 'filename')


def handle500(request):
    return JsonResponse({'message': 'File too large or there is a server error', 'status': 500})
