import mimetypes

from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseBadRequest, JsonResponse, StreamingHttpResponse
from django.shortcuts import render

from utils.utils import AESCrypto
from file.models import File

from .forms import UploadFileForm, handle_uploaded_file

# Create your views here.
def main_on_post_test(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES['file']
        handle_uploaded_file(request.FILES['file'])
        return JsonResponse({'message': 'OK', 'is_uploaded': True,
                             'url': file.encryptor.key_str, 'status': 200})
    return JsonResponse({'message': 'Bad request', 'is_uploaded': False,
                             'url': '', 'status': 400})

def main_on_post(request):
    file = request.FILES.get('file')
    if file is None:
        return HttpResponseBadRequest()
def main_on_get(request):
    return render(request, 'f1l3/index.html')


def main(request):
    if request.method == 'GET':
        return main_on_get(request)
    if request.method == 'POST':
        return main_on_post_test(request)

def download(request, fid, key):
    bytes_key = AESCrypto.str2key(key)
    kh = AESCrypto.key_hash(bytes_key)
    file = File.objects.filter(fid=fid, keyhash=kh).first()
    if file is None or not file.is_avail:
        return HttpResponseNotFound()
    content_type = mimetypes.guess_type(file.filename)
    resp = StreamingHttpResponse(file.iter_decrypt_read(bytes_key),
                                 status=200, content_type=content_type)
    resp['Content-Disposition'] = 'attachment; filename=' + file.filename
    return resp

def download_test(request, key):
    file = open('1.jpg', 'rb')
    content_type = mimetypes.guess_type('1.jpg')[0]
    aes = AESCrypto(key=AESCrypto.str2key(key))
    g = aes.iter_decrypt_file(file)
    resp = StreamingHttpResponse(g,
                                 status=200, content_type=content_type)
    resp['Content-Disposition'] = 'attachment; filename=' + '1.jpg'
    return resp
def handle500(request):
    return JsonResponse({'message': 'File too large or there is a server error', 'status': 500})