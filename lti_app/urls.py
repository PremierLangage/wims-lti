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
    path('lti/C<int:wims_pk>/', views.wims_class, name="wims_class"),
    path('lti/C<int:wims_pk>/A<int:activity_pk>/', views.wims_activity, name="wims_activity"),
    path('', views.lms, name="lms"),
    path('<int:lms_pk>/', views.wims, name="wims"),
    path('<int:lms_pk>/<int:wims_pk>/', views.classes, name="classes"),
    path('<int:lms_pk>/<int:wims_pk>/<int:wclass_pk>/', views.activities, name="sheets"),
]
