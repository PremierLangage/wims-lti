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
    path('api/lti_app/<int:lms_pk>/', views.get_wims, name="wims"),
    path('api/classes/<int:wims_pk>/', views.get_classes, name="classes"),
    path('api/activities/<int:wclass_pk>/', views.get_activities, name="activities"),
]
