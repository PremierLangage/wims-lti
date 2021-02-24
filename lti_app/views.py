# -*- coding: utf-8 -*-
#
#  views.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging

import requests
import wimsapi
from django.conf import settings
from django.contrib import messages
from django.http import (Http404, HttpRequest, HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from lti_app.enums import Role
from lti_app.exceptions import BadRequestException
from lti_app.models import GradeLinkExam, GradeLinkSheet, LMS, WIMS, WimsClass
from lti_app.utils import (MODE, check_custom_parameters, check_parameters, get_exam,
                           get_or_create_class, get_or_create_user, get_sheet, is_teacher,
                           is_valid_request, parse_parameters)


logger = logging.getLogger(__name__)

GET_ERROR_MSG = """405 Method Not Allowed: 'GET'<br><br>
This is usually caused by one of the following reason:
<ul>
    <li>Missing trailing slash '/' at the end of the URL
        (eg: "%s" instead of "%s").</li>
    <li>Used this URL outside of an LTI activity.</li>
</ul>
"""



def wims_class(request: HttpRequest, wims_pk: int) -> HttpResponse:
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
        - HttpResponse(status=502) if an error occured while communicating with the WIMS server.
        - HttpResponse(status=504) if the WIMS server could not be joined."""
    if request.method == "GET":
        uri = request.build_absolute_uri()
        return HttpResponseNotAllowed(["POST"], GET_ERROR_MSG % (uri[:-1], uri))
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: '%s'" % request.method)
    
    try:
        parameters = parse_parameters(request.POST)
        logger.info("Request received from '%s'" % request.META.get('HTTP_REFERER', "Unknown"))
        check_parameters(parameters)
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
        lms = LMS.objects.get(guid=parameters["tool_consumer_instance_guid"])
    except LMS.DoesNotExist:
        raise Http404("No LMS found with guid '%s'" % parameters["tool_consumer_instance_guid"])
    
    wapi = wimsapi.WimsAPI(wims_srv.url, wims_srv.ident, wims_srv.passwd)
    
    try:
        # Check that the WIMS server is available
        bol, response = wapi.checkident(verbose=True)
        if not bol:
            raise wimsapi.WimsAPIError(response['message'])
        
        # Check whether the class already exists, creating it otherwise
        wclass_db, wclass = get_or_create_class(lms, wims_srv, wapi, parameters)
        
        # Check whether the user already exists, creating it otherwise
        user_db, user = get_or_create_user(wclass_db, wclass, parameters)
        
        # Trying to authenticate the user on the WIMS server
        bol, response = wapi.authuser(wclass.qclass, wclass.rclass, user.quser)
        if not bol:  # pragma: no cover
            raise wimsapi.WimsAPIError(response['message'])
        url = response["home_url"] + ("&lang=%s" % wclass.lang)
    
    except wimsapi.WimsAPIError as e:  # WIMS server responded with ERROR
        logger.info(str(e))
        return HttpResponse(str(e), status=502)

    except BadRequestException as e:
        logger.info(str(e))
        return HttpResponseBadRequest(str(e))
    
    except requests.RequestException:
        logger.exception("Could not join the WIMS server '%s'" % wims_srv.url)
        return HttpResponse("Could not join the WIMS server '%s'" % wims_srv.url, status=504)
    
    return redirect(url)



def wims_sheet(request: HttpRequest, wims_pk: int, sheet_pk: int) -> HttpResponse:
    """Redirect the client to the WIMS server corresponding to <wims_pk> and sheet <sheet_pk>.

        Will retrieve/create the right WIMS' class/user according to informations in request.POST.

        Raises:
            - Http404 if no LMS corresponding to request.POST["tool_consumer_instance_guid"]
                has been found in the database.
            - PermissionDenied if the class corresponding to request.POST['context_id'] does not
                exists and roles in request.POST['context_id'] are not one of
                settings.ROLES_ALLOWED_CREATE_WIMS_CLASS.

        Returns:
            - HttpResponseRedirect redirecting the user to WIMS, logged in his WIMS' class.
            - HttpResponse(status=502) if an error occured while communicating with the WIMS.
            - HttpResponse(status=504) if the WIMS server could not be joined."""
    if request.method == "GET":
        uri = request.build_absolute_uri()
        return HttpResponseNotAllowed(["POST"], GET_ERROR_MSG % (uri[:-1], uri))
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: '%s'" % request.method)
    
    try:
        parameters = parse_parameters(request.POST)
        logger.info("Request received from '%s'" % request.META.get('HTTP_REFERER', "Unknown"))
        check_parameters(parameters)
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
        lms = LMS.objects.get(guid=parameters["tool_consumer_instance_guid"])
    except LMS.DoesNotExist:
        raise Http404("No LMS found with guid '%s'" % parameters["tool_consumer_instance_guid"])
    
    wapi = wimsapi.WimsAPI(wims_srv.url, wims_srv.ident, wims_srv.passwd)
    
    try:
        # Check that the WIMS server is available
        bol, response = wapi.checkident(verbose=True)
        if not bol:
            raise wimsapi.WimsAPIError(response['message'])
        
        # Get the class
        wclass_db = WimsClass.objects.get(wims=wims_srv, lms=lms,
                                          lms_guid=parameters['context_id'])
        
        try:
            wclass = wimsapi.Class.get(
                wims_srv.url, wims_srv.ident, wims_srv.passwd, wclass_db.qclass, wims_srv.rclass,
                timeout=settings.WIMSAPI_TIMEOUT
            )
        except wimsapi.WimsAPIError as e:
            if "not existing" in str(e):  # Class was deleted on the WIMS server
                qclass = wclass_db.qclass
                logger.info(("Deleting class (id : %d - wims id : %s - lms id : %s) as it was"
                             "deleted from the WIMS server")
                            % (wclass_db.id, str(wclass_db.qclass), str(wclass_db.lms_guid)))
                wclass_db.delete()
                return HttpResponseNotFound(
                    ("Class of ID %s could not be found on the WIMS server. Maybe it has been "
                     "deleted from the WIMS server. Use this LTI link on your LMS to create a new "
                     "WIMS class: %s")
                    % (qclass,
                       request.build_absolute_uri(reverse("lti:wims_class", args=[wims_pk])))
                )
            raise  # Unknown error (pragma: no cover)
        
        # Check whether the user already exists, creating it otherwise
        user_db, user = get_or_create_user(wclass_db, wclass, parameters)
        
        # Check whether the sheet already exists, creating it otherwise
        sheet_db, sheet = get_sheet(wclass_db, wclass, sheet_pk, parameters)
        if int(sheet.sheetmode) not in [1, 2]:  # not active or expired
            return HttpResponseForbidden("This WIMS sheet (%s) is currently unavailable (%s)"
                                         % (str(sheet.qsheet), MODE[int(sheet.sheetmode)]))
        
        # Storing the URL and ID to send the grade back to the LMS
        try:
            gl = GradeLinkSheet.objects.get(user=user_db, activity=sheet_db)
            gl.sourcedid = parameters["lis_result_sourcedid"]
            gl.url = parameters["lis_outcome_service_url"]
            gl.save()
        except GradeLinkSheet.DoesNotExist:
            GradeLinkSheet.objects.create(user=user_db, activity=sheet_db, lms=lms,
                                          sourcedid=parameters["lis_result_sourcedid"],
                                          url=parameters["lis_outcome_service_url"])
        
        # If user is a teacher, send all grade back to the LMS
        role = Role.parse_role_lti(parameters["roles"])
        if is_teacher(role):
            GradeLinkSheet.send_back_all(sheet_db)
        
        # Trying to authenticate the user on the WIMS server
        bol, response = wapi.authuser(wclass.qclass, wclass.rclass, user.quser)
        if not bol:  # pragma: no cover
            raise wimsapi.WimsAPIError(response['message'])
        
        params = "&lang=%s&module=adm%%2Fsheet&sh=%s" % (wclass.lang, str(sheet.qsheet))
        url = response["home_url"] + params
    
    except WimsClass.DoesNotExist as e:
        logger.info(str(e))
        return HttpResponseNotFound("Could not find class of id '%s'" % parameters['context_id'])
    
    except wimsapi.WimsAPIError as e:  # WIMS server responded with ERROR
        logger.info(str(e))
        return HttpResponse(str(e), status=502)
    
    except requests.RequestException:
        logger.exception("Could not join the WIMS server '%s'" % wims_srv.url)
        return HttpResponse("Could not join the WIMS server '%s'" % wims_srv.url, status=504)
    
    return redirect(url)



def wims_exam(request: HttpRequest, wims_pk: int, exam_pk: int) -> HttpResponse:
    """Redirect the client to the WIMS server corresponding to <wims_pk> and exam <exam_pk>.

        Will retrieve/create the right WIMS' class/user according to informations in request.POST.

        Raises:
            - Http404 if no LMS corresponding to request.POST["tool_consumer_instance_guid"]
                has been found in the database.
            - PermissionDenied if the class corresponding to request.POST['context_id'] does not
                exists and roles in request.POST['context_id'] are not one of
                settings.ROLES_ALLOWED_CREATE_WIMS_CLASS.

        Returns:
            - HttpResponseRedirect redirecting the user to WIMS, logged in his WIMS' class.
            - HttpResponse(status=502) if an error occured while communicating with the WIMS.
            - HttpResponse(status=504) if the WIMS server could not be joined."""
    if request.method == "GET":
        uri = request.build_absolute_uri()
        return HttpResponseNotAllowed(["POST"], GET_ERROR_MSG % (uri[:-1], uri))
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed: '%s'" % request.method)
    
    try:
        parameters = parse_parameters(request.POST)
        logger.info("Request received from '%s'" % request.META.get('HTTP_REFERER', "Unknown"))
        check_parameters(parameters)
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
        lms = LMS.objects.get(guid=parameters["tool_consumer_instance_guid"])
    except LMS.DoesNotExist:
        raise Http404("No LMS found with guid '%s'" % parameters["tool_consumer_instance_guid"])
    
    wapi = wimsapi.WimsAPI(wims_srv.url, wims_srv.ident, wims_srv.passwd)
    
    try:
        # Check that the WIMS server is available
        bol, response = wapi.checkident(verbose=True)
        if not bol:
            raise wimsapi.WimsAPIError(response['message'])
        
        # Get the class
        wclass_db = WimsClass.objects.get(wims=wims_srv, lms=lms,
                                          lms_guid=parameters['context_id'])
        
        try:
            wclass = wimsapi.Class.get(
                wims_srv.url, wims_srv.ident, wims_srv.passwd, wclass_db.qclass, wims_srv.rclass,
                timeout=settings.WIMSAPI_TIMEOUT
            )
        except wimsapi.WimsAPIError as e:
            if "not existing" in str(e):  # Class was deleted on the WIMS server
                qclass = wclass_db.qclass
                logger.info(("Deleting class (id : %d - wims id : %s - lms id : %s) as it was"
                             "deleted from the WIMS server")
                            % (wclass_db.id, str(wclass_db.qclass), str(wclass_db.lms_guid)))
                wclass_db.delete()
                return HttpResponseNotFound(
                    ("Class of ID %s could not be found on the WIMS server. Maybe it has been "
                     "deleted from the WIMS server. Use this LTI link on your LMS to create a new "
                     "WIMS class: %s")
                    % (qclass,
                       request.build_absolute_uri(reverse("lti:wims_class", args=[wims_pk])))
                )
            raise  # Unknown error (pragma: no cover)
        
        # Check whether the user already exists, creating it otherwise
        user_db, user = get_or_create_user(wclass_db, wclass, parameters)
        
        # Check whether the exam already exists, creating it otherwise
        exam_db, exam = get_exam(wclass_db, wclass, exam_pk, parameters)
        if int(exam.exammode) not in [1, 2]:  # not active or expired
            return HttpResponseForbidden("This exam (%s) is currently unavailable (%s)"
                                         % (str(exam.qexam), MODE[int(exam.exammode)]))
        
        # Storing the URL and ID to send the grade back to the LMS
        try:
            gl = GradeLinkExam.objects.get(user=user_db, activity=exam_db)
            gl.sourcedid = parameters["lis_result_sourcedid"]
            gl.url = parameters["lis_outcome_service_url"]
            gl.save()
        except GradeLinkExam.DoesNotExist:
            GradeLinkExam.objects.create(user=user_db, activity=exam_db, lms=lms,
                                         sourcedid=parameters["lis_result_sourcedid"],
                                         url=parameters["lis_outcome_service_url"])
        
        # If user is a teacher, send all grade back to the LMS
        role = Role.parse_role_lti(parameters["roles"])
        if is_teacher(role):
            GradeLinkExam.send_back_all(exam_db)
        
        # Trying to authenticate the user on the WIMS server
        bol, response = wapi.authuser(wclass.qclass, wclass.rclass, user.quser)
        if not bol:  # pragma: no cover
            raise wimsapi.WimsAPIError(response['message'])
        
        params = ("&lang=%s&module=adm%%2Fclass%%2Fexam&+job=student&+exam=%s"
                  % (wclass.lang, str(exam.qexam)))
        url = response["home_url"] + params
    
    except WimsClass.DoesNotExist as e:
        logger.info(str(e))
        return HttpResponseNotFound("Could not find class of id '%s'" % parameters['context_id'])
    
    except wimsapi.WimsAPIError as e:  # WIMS server responded with ERROR
        logger.info(str(e))
        return HttpResponse(str(e), status=502)
    
    except requests.RequestException:
        logger.exception("Could not join the WIMS server '%s'" % wims_srv.url)
        return HttpResponse("Could not join the WIMS server '%s'" % wims_srv.url, status=504)
    
    return redirect(url)



@require_GET
def lms(request) -> HttpResponse:
    """Display the list of available LMS."""
    return render(request, "lti_app/lms.html", {
        "LMS": LMS.objects.all(),
    })



@require_GET
def wims(request: HttpRequest, lms_pk: int) -> HttpResponse:
    """Display the list of available WIMS server that authorized <lms_pk>."""
    return render(request, "lti_app/wims.html", {
        "LMS":  LMS.objects.get(pk=lms_pk),
        "WIMS": WIMS.objects.filter(allowed_lms__pk=lms_pk),
    })



@require_GET
def classes(request: HttpRequest, lms_pk: int, wims_pk: int) -> HttpResponse:
    """Display the list the WIMS classes on the <wims_pk> server."""
    return render(request, "lti_app/classes.html", {
        "LMS":     LMS.objects.get(pk=lms_pk),
        "WIMS":    WIMS.objects.get(pk=wims_pk),
        "classes": WimsClass.objects.filter(wims__pk=wims_pk),
    })



@require_GET
def activities(request: HttpRequest, lms_pk: int, wims_pk: int, wclass_pk: int) -> HttpResponse:
    """Display the list of WIMS worksheet and exam in <wclass_pk> WIMS class."""
    try:
        class_srv = WimsClass.objects.get(pk=wclass_pk)
    except WimsClass.DoesNotExist:
        return HttpResponseNotFound("WimsClass of ID %d Was not found on the server." % wclass_pk)
    
    try:
        try:
            wclass = wimsapi.Class.get(
                class_srv.wims.url, class_srv.wims.ident, class_srv.wims.passwd, class_srv.qclass,
                class_srv.wims.rclass, timeout=settings.WIMSAPI_TIMEOUT
            )
        except wimsapi.WimsAPIError as e:
            # Delete the class if it does not exists on the server anymore
            if "class %s not existing" % str(class_srv.qclass) in str(e):
                logger.info(
                    (
                        "Deleting class of pk'%s' has the corresponding class of id '%s' does not "
                        "exists on the WIMS server '%s'  anymore")
                    % (str(class_srv.pk), str(class_srv.qclass), class_srv.wims.url)
                )
                class_srv.delete()
            raise  # WIMS server responded with ERROR (pragma: no cover)
        sheets = wclass.listitem(wimsapi.Sheet)
        
        for s in sheets:
            s.lti_url = request.build_absolute_uri(
                reverse("lti:wims_sheet", args=[wims_pk, s.qsheet])
            )
            s.sheetmode = MODE[int(s.sheetmode)]
        
        exams = wclass.listitem(wimsapi.Exam)
        for e in exams:
            e.lti_url = request.build_absolute_uri(
                reverse("lti:wims_exam", args=[wims_pk, e.qexam])
            )
            e.exammode = MODE[int(e.exammode)]
    
    except wimsapi.InvalidResponseError as e:  # WIMS server responded with ERROR (pragma: no cover)
        logger.info(str(e), str(e.response))
        messages.error(request, 'The WIMS server returned a badly formatted response: ' + str(e))
    
    except wimsapi.WimsAPIError as e:  # WIMS server responded with ERROR (pragma: no cover)
        logger.info(str(e))
        messages.error(request, 'The WIMS server returned an error: ' + str(e))
    
    except requests.RequestException:  # WIMS server responded with ERROR (pragma: no cover)
        logger.exception("Could not join the WIMS server '%s'" % class_srv.wims.url)
        messages.error(request, 'Could not join the WIMS server')
    
    else:  # No exception occured
        return render(request, "lti_app/activities.html", {
            "LMS":    LMS.objects.get(pk=lms_pk),
            "WIMS":   WIMS.objects.get(pk=wims_pk),
            "class":  WimsClass.objects.get(pk=wclass_pk),
            "sheets": sheets,
            "exams":  exams,
        })
    
    # An exception occured
    return redirect('lti:classes', lms_pk=lms_pk, wims_pk=wims_pk)  # pragma: no cover
