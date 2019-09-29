from django.urls import path
from .views import main, download_test
urlpatterns = [
    path('', main),
    path('d_test/<slug:key>/', download_test)
]
