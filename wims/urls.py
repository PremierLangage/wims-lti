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
    path('dns/<dns:dns>/', views.from_dns, name="from_dns"),
    path('id/<int:pk>/', views.from_id, name="from_id"),
    path('list/', views.ls, name="ls"),
    path('', views.about, name="about"),
    path('about/<str:lang>/', views.about, name="about"),
]
