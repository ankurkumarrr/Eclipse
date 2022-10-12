from django.conf.urls import url
from . import views
from django.urls import path

urlpatterns = [
    url('^$',views.home),
    path('imageselection/',views.imageselection),
    path('imageselection/encode',views.encodepage),
    path('imageselection/decode',views.decodepage),
    path('imageselection/authcode',views.authcode),
    path('imageselection/check',views.check),
]
