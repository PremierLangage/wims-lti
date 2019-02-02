# -*- coding: utf-8 -*-
#
#  views.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging

from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
from wimsapi import AdmRawError, WimsAPI

from wims.exceptions import BadRequestException
from wims.models import LMS, WIMS
from wims.utils import (get_or_create_class, get_or_create_user, lti_request_is_valid,
                        parse_parameters)


logger = logging.getLogger(__name__)



def redirect_to_wims(request, wims_srv):
    """Redirect the client to the WIMS server corresponding to <wims_srv>.
    
    Will retrieve/create the right WIMS' class/user according to informations in request.POST.
    
    Raises:
        - Http404 if no LMS corresponding to request.POST["tool_consumer_instance_guid"]
                  has been found in the database.
        - PermissionDenied if the class corresponding to request.POST['context_id'] does not exists
                           and roles in request.POST['context_id'] are not one of
                           settings.ROLES_ALLOWED_CREATE_WIMS_CLASS.
    
    Returns:
        - HttpResponseRedirect redirecting the user to WIMS, logged in his WIMS' class.
        - HttpResponse(status=421) if an error occured while communicating with the WIMS server."""
    
    parameters = parse_parameters(request.POST)
    
    # Retrieve LMS
    try:
        lms = LMS.objects.get(uuid=parameters["tool_consumer_instance_guid"])
    except LMS.DoesNotExist:
        raise Http404("No LMS found with uuid '%s'" % parameters["tool_consumer_instance_guid"])
    wapi = WimsAPI(wims_srv.url, wims_srv.ident, wims_srv.passwd)
    
    try:
        # Check that the WIMS server is available
        bol, response = wapi.checkident(verbose=True)
        if not bol:
            raise AdmRawError(response['message'])
        
        # Check whether the class already exists, creating it otherwise, can raise AdmRawError
        wclass_db, wclass = get_or_create_class(lms, wims_srv, wapi, parameters)
        
        # Check whether the user already exists, creating it otherwise, can raise AdmRawError
        _, user = get_or_create_user(lms, wclass_db, wclass, parameters)
        
        # Trying to authenticate the user on the WIMS server
        bol, response = wapi.authuser(wclass.qclass, wclass.rclass, user.quser)
        if not bol:
            raise AdmRawError(response['message'])
    
    except AdmRawError as e:  # WIMS server responded with ERROR
        logger.info(str(e))
        return HttpResponse(str(e), status=421)
    
    return redirect(response["home_url"])



@csrf_exempt
def from_dns(request, dns):
    """Use the DNS to retrieve the WIMS model from the database."""
    if request.method == "GET":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: 'GET'. Did you forget "
                                                "trailing '/' ?")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: '%s'" % request.method)
    
    try:
        lti_request_is_valid(request)
    except BadRequestException as e:
        logger.info(str(e))
        return HttpResponseBadRequest(str(e))
    
    try:
        wims = WIMS.objects.get(dns=dns)
    except WIMS.DoesNotExist:
        raise Http404("Unknown WIMS server '%s'" % dns)
    
    return redirect_to_wims(request, wims)



@csrf_exempt
def from_id(request, pk):
    """Use the PK to retrieve the WIMS model from the database."""
    if request.method == "GET":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: 'GET'. Did you forget "
                                                "trailing '/' ?")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: '%s'" % request.method)
    
    try:
        lti_request_is_valid(request)
    except BadRequestException as e:
        logger.info(str(e))
        return HttpResponseBadRequest(str(e))
    
    try:
        wims = WIMS.objects.get(pk=pk)
    except WIMS.DoesNotExist:
        raise Http404("Unknown WIMS server of id '%d'" % pk)
    
    return redirect_to_wims(request, wims)



@csrf_exempt
def list(request):
    """List all available LMS and WIMS server."""
    wserver = WIMS.objects.all()
    for w in wserver:
        w.lti_url = request.build_absolute_uri(reverse("wims:from_dns", args=[w.dns]))
    
    return render(request, 'wims/list.html', {
        "LMS":  LMS.objects.all(),
        "WIMS": wserver,
    })
