# -*- coding: utf-8 -*-
#
#  urls.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#


from django.urls import path

from api import views


app_name = "api"

urlpatterns = [
    path('api/', views.get_wims, name="wims_activity"),
]
