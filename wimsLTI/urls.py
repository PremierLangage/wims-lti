# -*- coding: utf-8 -*-
#
#  urls.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>


from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('wims.urls', namespace='wims'))
]
