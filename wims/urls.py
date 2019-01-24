# -*- coding: utf-8 -*-
#
#  urls.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#


from django.urls import path, register_converter

from wims import converters, views


register_converter(converters.DNSConverter, 'dns')

app_name = "wims"

urlpatterns = [
    path('<dns:dns>/', views.from_dns),
    path('<int:pk>/', views.from_id),
]
