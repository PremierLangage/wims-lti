# -*- coding: utf-8 -*-
#
#  urls.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#
from django.conf import settings
from django.urls import path

from lti_app import views
from lti_app.tests import views as test_views


app_name = "lti"

urlpatterns = [
    path('lti/C<int:wims_pk>/', views.wims_class, name="wims_class"),
    path('lti/C<int:wims_pk>/S<int:sheet_pk>/', views.wims_sheet, name="wims_sheet"),
    path('lti/C<int:wims_pk>/E<int:exam_pk>/', views.wims_exam, name="wims_exam"),
    path('', views.lms, name="lms"),
    path('<int:lms_pk>/', views.wims, name="wims"),
    path('<int:lms_pk>/<int:wims_pk>/', views.classes, name="classes"),
    path('<int:lms_pk>/<int:wims_pk>/<int:wclass_pk>/', views.activities, name="sheets"),
]

if settings.TESTING:  # pragma: no cover
    urlpatterns += [
        path('test/xml_ok/', test_views.xml_ok, name="test_xml_ok"),
        path('test/xml_error/', test_views.xml_error_response, name="test_xml_error"),
        path('test/xml_badly_formatted/', test_views.xml_badly_formatted,
             name="xml_badly_formatted"),
    ]
