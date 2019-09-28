import mimetypes
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render
from utils.utils import AESCrypto

from file.models import File
from .forms import UploadFileForm, handle_uploaded_file
# Create your views here.
def main_on_post_test(request):
    form = UploadFileForm(request.POST, request.FILES)
    print(form.is_valid())
    if form.is_valid():
        handle_uploaded_file(request.FILES['file'])
        return HttpResponse('yes')

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
    resp = HttpResponse(file.iter_decrypt_read(), status=200, content_type=content_type)
    resp['Content-Disposition'] = 'attachment; filename=' + file.filename
    return resp