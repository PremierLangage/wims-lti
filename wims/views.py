# -*- coding: utf-8 -*-
#
#  views.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from wimsapi import AdmRawError, WimsAPI

from wims.exceptions import BadRequestException
from wims.models import LMS, WIMS
from wims.utils import (check_parameters, get_or_create_class, get_or_create_user,
                        is_valid_request, parse_parameters)


logger = logging.getLogger(__name__)



def lti_request_is_invalid(request):
    """Returns None if the  LTI request is valid, an HttpResponseBadRequest
    otherwise."""
    parameters = parse_parameters(request.POST)
    
    try:
        logger.info("Request received from '%s'" % request.META['HTTP_REFERER'])
        check_parameters(parameters)
        is_valid_request(request)
    except BadRequestException as e:
        logger.info(str(e))
        return HttpResponseBadRequest(str(e))



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
    lms = get_object_or_404(LMS, uuid=parameters["tool_consumer_instance_guid"])
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
    
    return redirect(response["home"])



@csrf_exempt
def from_dns(request, dns):
    """Use the DNS to retrieve the WIMS model from the database."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed")
    
    return (lti_request_is_invalid(request)
            or redirect_to_wims(request, get_object_or_404(WIMS, dns=dns)))



@csrf_exempt
def from_id(request, pk):
    """Use the PK to retrieve the WIMS model from the database."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed")
    
    return (lti_request_is_invalid(request)
            or redirect_to_wims(request, get_object_or_404(WIMS, pk=pk)))
