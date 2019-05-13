# -*- coding: utf-8 -*-
#
#  urls.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#


from django.urls import path

from lti_app import views


app_name = "lti"

urlpatterns = [
    path('<int:wims_pk>/', views.wims_class, name="wims_class"),
    path('<int:wims_pk>/<int:activity_pk>/', views.wims_activity, name="wims_activity"),
    path('links/', views.links, name="links"),
]
