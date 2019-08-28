# -*- coding: utf-8 -*-
#
#  urls.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>


from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('lti_app.urls', namespace='lti')),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
]
