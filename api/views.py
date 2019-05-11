# -*- coding: utf-8 -*-
#
#  views.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging

from django.http import (Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET
from wimsapi import AdmRawError, Class, WimsAPI

from lti_app.exceptions import BadRequestException
from api.models import Activity, WIMS, WimsClass


logger = logging.getLogger(__name__)




@require_GET
def get_wims(request, lms_pk):
    return JsonResponse(WIMS.objects.filter(lms__pk=lms_pk))



@require_GET
def get_classes(request, wims_pk):
    return JsonResponse(WimsClass.objects.filter(wims__pk=wims_pk))



@require_GET
def get_activity(request, wims_pk, wclass_pk, passwd):
    srv_class = get_object_or_404(WimsClass, wims=wims_pk, wclass=wclass_pk)
    
    try:
        wclass = Class.get(srv_class.wims.url, srv_class.wims.ident, srv_class.wims.passwd,
                           srv_class.qclass, srv_class.wims.rclass)
    except AdmRawError as e:  # WIMS server responded with ERROR
        logger.info(str(e))
        return HttpResponse(str(e), status=502)
    
    if wclass.password != passwd:
        return HttpResponseForbidden("Invalid password")
    
    return JsonResponse(Activity.objects.filter(wclass=srv_class))
