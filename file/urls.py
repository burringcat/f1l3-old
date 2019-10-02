from django.urls import path
from .views import main, download, download_no_ext, upload
urlpatterns = [
    path('', main),
    path('u/', upload, name='upload'),
    path('<slug:key>.<slug:ext>', download),
    path('<slug:key>', download_no_ext)
]
