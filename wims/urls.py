# -*- coding: utf-8 -*-
#
#  urls.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#


from django.urls import path

from wims import views


app_name = "wims"

urlpatterns = [
    path('<int:wims_pk>/', views.wims_class, name="wims_class"),
    path('<int:wims_pk>/<int:activity_pk>', views.wims_activity, name="wims_activity"),
]
