from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import reverse
from django.conf import settings
from ipware import get_client_ip

from utils.utils import userutils

from .models import F1L3User, IPAddress


# Create your views here.
def f1l3_auth(request) -> F1L3User:
    user: F1L3User = F1L3User.objects.filter(user=request.user).first() or \
                     F1L3User.auth_by_token(request.POST.get('token'))
    return user


def register(request):
    rarg = lambda n: request.POST.get(n)
    username = rarg('username')
    password = rarg('password')
    ip_address, is_routable = get_client_ip(request)
    if is_routable is False and settings.DEBUG is False:
        return HttpResponseBadRequest('registering from private ip while DEBUG is False.')
    if not all((username, password)):
        return HttpResponseBadRequest()
    duplicated = False
    try:
        User.objects.get(username=username)
        duplicated = True
    except User.DoesNotExist:
        pass
    if duplicated:
        return HttpResponse('Username exists')
    F1L3User.objects.create(
        user=User.objects.create(username=username, password=password),
        ip=IPAddress.objects.get_or_create(address=ip_address)[0]
    )
    return reverse(viewname='homepage')


def generate_token(request):
    user: F1L3User = f1l3_auth(request)
    if user is None:
        return HttpResponseBadRequest()
    token = user.generate_token()
    user.token_hash = user.generate_token_hash(token)
    user.save()
    return HttpResponse(token)


def login_user(request):
    user: User = authenticate(request)
    if user is not None:
        login(request, user)
    return reverse('homepage')


def logout_user(request):
    logout(request)
    return reverse('homepage')


def command(request):
    user = f1l3_auth(request)
    if user is None:
        return HttpResponseForbidden()
    cmd = request.POST.get('cmd')
    args = request.POST.get('args', '')
    arg_list = args.split(',')
    cmds = userutils.SerializableCommands(user)
    return JsonResponse(cmds.exec(cmd, *arg_list))