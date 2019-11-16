
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from photo.views import me, index, join, AlbumView,test

urlpatterns = [
    path('', index),
    path('in/', join),
    path('me/', me),
    path('test/', test),
    url('^album$', AlbumView.post),
    url('album/(.*)', AlbumView.as_view()),
    url('download/(.*)', AlbumView.download),
    path('admin/', admin.site.urls),
]
