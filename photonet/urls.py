
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from photo.views import me, index, join, AlbumView

urlpatterns = [
    path('', index),
    path('in/', join),
    path('me/', me),
    path('album/', AlbumView.as_view()),
    url('album/(.*)', AlbumView.as_view()),
    url('download/(.*)', AlbumView.download),
    path('admin/', admin.site.urls),
]
