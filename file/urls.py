from django.urls import path
from .views import main, download
urlpatterns = [
    path('', main),
    path('<slug:key>.<slug:ext>', download)
]
