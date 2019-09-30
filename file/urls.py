from django.urls import path
from .views import main, download
urlpatterns = [
    path('', main),
    path('d/<slug:fid>/k/<slug:key>/<str:filename>', download)
]
