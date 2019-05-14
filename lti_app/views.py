import logging

import requests
import wimsapi
from django.http import (Http404, HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed,
                         HttpResponseNotFound)
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from api.models import GradeLink, LMS, WIMS, WimsClass
from api.utils import get_or_create_class, get_or_create_user, get_sheet
from lti_app.exceptions import BadRequestException
from lti_app.utils import (check_custom_parameters, check_parameters, is_valid_request,
                           parse_parameters)


logger = logging.getLogger(__name__)



def wims_class(request, wims_pk):
    """Redirect the client to the WIMS server corresponding to <pk>.

    Will retrieve/create the right WIMS' class/user according to informations in request.POST.

    Raises:
        - Http404 if no LMS corresponding to request.POST["tool_consumer_instance_guid"]
                  has been found in the database.
        - PermissionDenied if the class corresponding to request.POST['context_id'] does not exists
                           and roles in request.POST['context_id'] are not one of
                           settings.ROLES_ALLOWED_CREATE_WIMS_CLASS.

    Returns:
        - HttpResponseRedirect redirecting the user to WIMS, logged in his WIMS' class.
        - HttpResponse(status=502) if an error occured while communicating with the WIMS server."""
    if request.method == "GET":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: 'GET'. Did you forget "
                                                "trailing '/' ?")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: '%s'" % request.method)
    
    try:
        parameters = parse_parameters(request.POST)
        logger.info("Request received from '%s'" % request.META.get('HTTP_REFERER', "Unknown"))
        check_parameters(parameters)
        check_custom_parameters(parameters)
        is_valid_request(request)
    except BadRequestException as e:
        logger.info(str(e))
        return HttpResponseBadRequest(str(e))
    
    # Retrieve the WIMS server
    try:
        wims_srv = WIMS.objects.get(pk=wims_pk)
    except WIMS.DoesNotExist:
        raise Http404("Unknown WIMS server of id '%d'" % wims_pk)
    
    # Retrieve the LMS
    try:
        lms = LMS.objects.get(uuid=parameters["tool_consumer_instance_guid"])
    except LMS.DoesNotExist:
        raise Http404("No LMS found with uuid '%s'" % parameters["tool_consumer_instance_guid"])
    
    wapi = wimsapi.WimsAPI(wims_srv.url, wims_srv.ident, wims_srv.passwd)
    
    try:
        # Check that the WIMS server is available
        bol, response = wapi.checkident(verbose=True)
        if not bol:
            raise wimsapi.AdmRawError(response['message'])
        
        # Check whether the class already exists, creating it otherwise
        wclass_db, wclass = get_or_create_class(lms, wims_srv, wapi, parameters)
        
        # Check whether the user already exists, creating it otherwise
        _, user = get_or_create_user(wclass_db, wclass, parameters)
        
        # Trying to authenticate the user on the WIMS server
        bol, response = wapi.authuser(wclass.qclass, wclass.rclass, user.quser)
        if not bol:  # pragma: no cover
            raise wimsapi.AdmRawError(response['message'])
        url = response["home_url"] + ("&lang=%s" % wclass.lang)
    
    except wimsapi.AdmRawError as e:  # WIMS server responded with ERROR
        logger.info(str(e))
        return HttpResponse(str(e), status=502)
    
    except requests.RequestException:
        logger.exception("Could not join the WIMS server '%s'" % wims_srv.url)
        return HttpResponse("Could not join the WIMS server '%s'" % wims_srv.url, status=504)
    
    return redirect(url)



def wims_activity(request, wims_pk, activity_pk):
    if request.method == "GET":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: 'GET'. Did you forget "
                                                "trailing '/' ?")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: '%s'" % request.method)
    
    try:
        parameters = parse_parameters(request.POST)
        logger.info("Request received from '%s'" % request.META.get('HTTP_REFERER', "Unknown"))
        check_parameters(parameters)
        check_custom_parameters(parameters)
        is_valid_request(request)
    except BadRequestException as e:
        logger.info(str(e))
        return HttpResponseBadRequest(str(e))
    
    # Retrieve the WIMS server
    try:
        wims_srv = WIMS.objects.get(pk=wims_pk)
    except WIMS.DoesNotExist:
        raise Http404("Unknown WIMS server of id '%d'" % wims_pk)
    
    # Retrieve the LMS
    try:
        lms = LMS.objects.get(uuid=parameters["tool_consumer_instance_guid"])
    except LMS.DoesNotExist:
        raise Http404("No LMS found with uuid '%s'" % parameters["tool_consumer_instance_guid"])
    
    wapi = wimsapi.WimsAPI(wims_srv.url, wims_srv.ident, wims_srv.passwd)
    
    try:
        # Check that the WIMS server is available
        bol, response = wapi.checkident(verbose=True)
        if not bol:
            raise wimsapi.AdmRawError(response['message'])
        
        # Get the class
        wclass_db = WimsClass.objects.get(wims=wims_srv, lms=lms,
                                          lms_uuid=parameters['context_id'])
        wclass = wimsapi.Class.get(wims_srv.url, wims_srv.ident, wims_srv.passwd, wclass_db.qclass,
                                   wims_srv.rclass)
        
        # Check whether the user already exists, creating it otherwise
        user_db, user = get_or_create_user(wclass_db, wclass, parameters)
        
        # Check whether the sheet already exists, creating it otherwise
        activity, sheet = get_sheet(wclass_db, wclass, activity_pk, parameters)
        raise Exception(str(parameters))
        # Storing the URL and ID to send the grade back to the LMS
        try:
            gl = GradeLink.objects.get(user=user_db, activity=activity)
            gl.sourcedid = parameters["lis_result_sourcedid"]
            gl.save()
        except GradeLink.DoesNotExist:
            GradeLink.objects.create(user=user_db, activity=activity,
                                     sourcedid=parameters["lis_result_sourcedid"],
                                     url=parameters["lis_outcome_service_url"])
        
        # Trying to authenticate the user on the WIMS server
        bol, response = wapi.authuser(wclass.qclass, wclass.rclass, user.quser)
        if not bol:  # pragma: no cover
            raise wimsapi.AdmRawError(response['message'])
        
        url = (response["home_url"]
               + "&lang=%s&module=adm%%2Fsheet&sh=%s" % (wclass.lang, str(sheet.qsheet)))
    
    except WimsClass.DoesNotExist as e:
        logger.info(str(e))
        return HttpResponseNotFound("Could not find class of id '%s'" % parameters['context_id'])
    
    except wimsapi.AdmRawError as e:  # WIMS server responded with ERROR
        logger.info(str(e))
        return HttpResponse(str(e), status=502)
    
    except requests.RequestException:
        logger.exception("Could not join the WIMS server '%s'" % wims_srv.url)
        return HttpResponse("Could not join the WIMS server '%s'" % wims_srv.url, status=504)
    
    return redirect(url)



@require_GET
def links(request):
    return render(request, "lti_app/links.html", {
        "LMS": LMS.objects.all(),
    })
