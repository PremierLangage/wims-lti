# -*- coding: utf-8 -*-
#
#  views.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging

import requests
from django.http import (HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,
                         JsonResponse)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_GET
from wimsapi import AdmRawError, Class, Sheet

from api.models import WIMS, WimsClass


logger = logging.getLogger(__name__)



@require_GET
def get_wims(request, lms_pk):
    return JsonResponse({
        "content": [w.serialize(request) for w in WIMS.objects.filter(allowed_lms__pk=lms_pk)]
    })



@require_GET
def get_classes(request, wims_pk):
    return JsonResponse({
        "content": [c.serialize() for c in WimsClass.objects.filter(wims__pk=wims_pk)]
    })



@require_GET
def get_activities(request, wclass_pk):
    class_srv = get_object_or_404(WimsClass, pk=wclass_pk)
    
    passwd = request.GET.get("password", None)
    if passwd is None:
        return HttpResponseBadRequest("Missing parameter: 'password'")
    
    try:
        wclass = Class.get(class_srv.wims.url, class_srv.wims.ident, class_srv.wims.passwd,
                           class_srv.qclass, class_srv.wims.rclass)
        if wclass.password != passwd:
            return HttpResponseForbidden("Invalid password")
        
        sheets = [s.infos for s in wclass.listitem(Sheet)]
        sheets = [{
            "title":   s["sheet_title"],
            "id":      s["query_sheet"],
            'lti_url': request.build_absolute_uri(
                reverse("lti:wims_activity", args=[class_srv.wims.pk, s["query_sheet"]])
            ),
        } for s in sheets]
        
        return JsonResponse({
            "content": sheets
        })
    except AdmRawError as e:  # WIMS server responded with ERROR (pragma: no cover)
        logger.info(str(e))
        return HttpResponse(str(e), status=502)
    except requests.RequestException:
        logger.exception("Could not join the WIMS server '%s'" % class_srv.wims.url)
        return HttpResponse("Could not join the WIMS server '%s'" % class_srv.wims.url, status=504)
