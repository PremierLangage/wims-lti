# -*- coding: utf-8 -*-
#
#  utils.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging
import os
import random
import string
from datetime import datetime
from string import ascii_letters, digits
from typing import Any, Dict, Tuple

import oauth2
import wimsapi
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpRequest
from lti.contrib.django import DjangoToolProvider
from wimsapi import Exam, Sheet

from lti_app.enums import Role
from lti_app.exceptions import BadRequestException
from lti_app.models import LMS, WIMS, WimsClass, WimsExam, WimsSheet, WimsUser
from lti_app.validator import CustomParameterValidator, RequestValidator, validate


logger = logging.getLogger(__name__)

MODE = ["pending", "active", "expired", "hidden"]



def is_teacher(role: Role) -> bool:
    """Returns whether role is considered as a teacher."""
    return not set(role).isdisjoint(settings.ROLES_ALLOWED_CREATE_WIMS_CLASS)



def is_valid_request(request: HttpRequest) -> bool:
    """Check whether the request is valid and is accepted by oauth2.

    Raises:
        - api.exceptions.BadRequestException if the request is invalid.
        - django.core.exceptions.PermissionDenied if signature check failed."""
    parameters = parse_parameters(request.POST)
    
    if parameters['lti_message_type'] != 'basic-lti-launch-request':
        raise BadRequestException("LTI request is invalid, parameter 'lti_message_type' "
                                  "must be equal to 'basic-lti-launch-request'")
    
    try:
        tool_provider = DjangoToolProvider.from_django_request(request=request)
        request_is_valid = tool_provider.is_valid_request(RequestValidator())
    except oauth2.Error as e:  # pragma: no cover
        logger.warning("Oauth authentication failed : %s" % str(e))
        request_is_valid = False
    
    if not request_is_valid:
        logger.debug("LTI Authentification aborted: signature check failed with parameters : %s",
                     parameters)
        raise PermissionDenied("Invalid request: signature check failed.")
    return True



def check_parameters(param: Dict[str, Any]) -> None:
    """Check that mandatory parameters are present (either by LTI
    specification or required by this app)

    Raises api.exceptions.BadRequestException if this is not the case."""
    
    if not all([param[i] is not None for i in settings.LTI_MANDATORY]):
        missing = [i for i in settings.LTI_MANDATORY if param[i] is None]
        raise BadRequestException("LTI request is invalid, missing parameter(s): "
                                  + str(missing))
    
    if not all([param[i] is not None for i in settings.WIMSLTI_MANDATORY]):
        missing = [i for i in settings.WIMSLTI_MANDATORY if param[i] is None]
        raise BadRequestException("LTI request is invalid, WIMS LTI require parameter(s): "
                                  + str(missing))



def check_custom_parameters(params: Dict[str, Any]) -> None:
    """Checks that custom parameters, if given, are properly formatted.

    Raises api.exceptions.BadRequestException if this is not the case."""
    validate(
        CustomParameterValidator.email_validator, params['custom_class_email'],
        "Invalid parameter 'custom_class_email' (%s): invalid email" % params['custom_class_email']
    )
    validate(
        CustomParameterValidator.lang_validator, params['custom_class_lang'],
        ("Invalid parameter 'custom_class_lang' ('%s'):  not a valid 'ISO 3166-1 alpha-2' code"
         % params['custom_class_lang'])
    )
    validate(
        CustomParameterValidator.level_validator, params['custom_class_level'],
        ("Invalid parameter 'custom_class_level' ('%s'): not one of %s"
         % (params['custom_class_level'], wimsapi.wclass.LEVEL))
    )
    validate(
        CustomParameterValidator.expiration_validator, params['custom_class_expiration'],
        (("Invalid parameter 'custom_class_expiration' ('%s'): must be formatted as 'YYYYMMDD' and "
          "be more than a month and  less than a year from now")
         % params['custom_class_expiration'])
    )
    validate(
        CustomParameterValidator.limit_validator, params['custom_class_limit'],
        ("Invalid parameter 'custom_class_limit' ('%s'): Must be in [1, 300]"
         % params['custom_class_limit'])
    )



def parse_parameters(p: Dict[str, Any]) -> Dict[str, Any]:
    """Returns the a dictionnary of the LTI request parameters,
    replacing missing parameters with None.

    Raises api.exceptions.BadRequestException if one of the parameters
    starts with 'custom_custom'."""
    
    custom_custom = [key for key in p if key.startswith("custom_custom")]
    if custom_custom:
        raise BadRequestException("Parameter(s) starting with 'custom_custom' found in the request,"
                                  " maybe your LMS automatically prefix custom LTI parameters with "
                                  "'custom_': %s" % str(custom_custom))
    
    return {
        'lti_version':                            p.get('lti_version'),
        'context_id':                             p.get('context_id'),
        'context_label':                          p.get('context_label'),
        'context_title':                          p.get('context_title'),
        'context_type':                           p.get('context_type'),
        'custom_canvas_account_id':               p.get('custom_canvas_account_id'),
        'custom_canvas_account_sis_id':           p.get('custom_canvas_account_sis_id'),
        'custom_canvas_api_domain':               p.get('custom_canvas_api_domain'),
        'custom_canvas_course_id':                p.get('custom_canvas_course_id'),
        'custom_canvas_enrollment_state':         p.get('custom_canvas_enrollment_state'),
        'custom_canvas_membership_roles':         p.get('custom_canvas_membership_roles', ''),
        'custom_canvas_user_id':                  p.get('custom_canvas_user_id'),
        'custom_canvas_user_login_id':            p.get('custom_canvas_user_login_id'),
        'launch_presentation_css_url':            p.get('launch_presentation_css_url'),
        'launch_presentation_document_target':    p.get('launch_presentation_document_target'),
        'launch_presentation_height':             p.get('launch_presentation_height'),
        'launch_presentation_locale':             p.get('launch_presentation_locale'),
        'launch_presentation_return_url':         p.get('launch_presentation_return_url'),
        'launch_presentation_width':              p.get('launch_presentation_width'),
        'lis_course_offering_sourcedid':          p.get('lis_course_offering_sourcedid'),
        'lis_outcome_service_url':                p.get('lis_outcome_service_url'),
        'lis_result_sourcedid':                   p.get('lis_result_sourcedid'),
        'lis_person_contact_email_primary':       p.get('lis_person_contact_email_primary'),
        'lis_person_name_family':                 p.get('lis_person_name_family'),
        'lis_person_name_full':                   p.get('lis_person_name_full'),
        'lis_person_name_given':                  p.get('lis_person_name_given'),
        'lis_person_sourcedid':                   p.get('lis_person_sourcedid'),
        'lti_message_type':                       p.get('lti_message_type'),
        'oauth_consumer_key':                     p.get('oauth_consumer_key'),
        'oauth_consumer_secret':                  p.get('oauth_consumer_secret'),
        'oauth_signature_method':                 p.get('oauth_signature_method'),
        'oauth_timestamp':                        p.get('oauth_timestamp'),
        'oauth_nonce':                            p.get('oauth_nonce'),
        'oauth_version':                          p.get('oauth_version'),
        'oauth_signature':                        p.get('oauth_signature'),
        'oauth_callback':                         p.get('oauth_callback'),
        'resource_link_description':              p.get('resource_link_description'),
        'resource_link_id':                       p.get('resource_link_id'),
        'resource_link_title':                    p.get('resource_link_title'),
        'roles':                                  p.get('roles', ''),
        'selection_directive':                    p.get('selection_directive'),
        'tool_consumer_info_product_family_code': p.get('tool_consumer_info_product_family_code'),
        'tool_consumer_info_version':             p.get('tool_consumer_info_version'),
        'tool_consumer_instance_contact_email':   p.get('tool_consumer_instance_contact_email'),
        'tool_consumer_instance_description':     p.get('tool_consumer_instance_description'),
        'tool_consumer_instance_guid':            p.get('tool_consumer_instance_guid'),
        'tool_consumer_instance_name':            p.get('tool_consumer_instance_name'),
        'tool_consumer_instance_url':             p.get('tool_consumer_instance_url'),
        'user_id':                                p.get('user_id'),
        'user_image':                             p.get('user_image'),
        'custom_class_name':                      p.get('custom_class_name'),
        'custom_class_institution':               p.get('custom_class_institution'),
        'custom_class_email':                     p.get('custom_class_email'),
        'custom_class_lang':                      p.get('custom_class_lang'),
        'custom_class_expiration':                p.get('custom_class_expiration'),
        'custom_class_limit':                     p.get('custom_class_limit'),
        'custom_class_level':                     p.get('custom_class_level'),
        'custom_class_css':                       p.get('custom_class_css'),
        'custom_supervisor_lastname':             p.get('custom_supervisor_lastname'),
        'custom_supervisor_firstname':            p.get('custom_supervisor_firstname'),
    }



def create_supervisor(params: Dict[str, Any]) -> wimsapi.User:
    """Create an instance of wimapi.User corresponding to the class' supervisor with the given LTI
    request's parameters."""
    supervisor = {
        "quser":     "supervisor",
        "lastname":  (params['custom_supervisor_lastname']
                      or ("" if params['custom_supervisor_firstname'] else "Supervisor")),
        "firstname": params['custom_supervisor_firstname'] or "",
        "password":  ''.join(random.choice(ascii_letters + digits) for _ in range(10)),
        "email":     params["lis_person_contact_email_primary"],
    }
    return wimsapi.User(**supervisor)



def create_class(wims_srv: WIMS, params: Dict[str, Any]) -> wimsapi.Class:
    """Create an instance of wimsapi.Class with the given LTI request's parameters and wclass_db."""
    
    wclass_dic = {
        "name":        params["custom_class_name"] or params["context_title"],
        "institution": (params["custom_class_institution"]
                        or params["tool_consumer_instance_description"]),
        "email":       params["custom_class_email"] or params[
            "lis_person_contact_email_primary"],
        "lang":        params["custom_class_lang"] or params["launch_presentation_locale"][:2],
        "expiration":  (params["custom_class_expiration"]
                        or (datetime.now() + wims_srv.expiration).strftime("%Y%m%d")),
        "limit":       params["custom_class_limit"] or wims_srv.class_limit,
        "level":       params["custom_class_level"] or "H4",
        "css":         params["custom_class_css"] or "",
        "password":    ''.join(random.choice(ascii_letters + digits) for _ in range(10)),
        "supervisor":  create_supervisor(params),
        "rclass":      wims_srv.rclass,
    }
    return wimsapi.Class(**wclass_dic)



def generate_mail(wclass_db: WimsClass, wclass: wimsapi.Class) -> Tuple[str, str]:
    """Returns the title and the body of the credentials mail corresponding to
    the language of the class."""
    
    params = {
        "qclass":              wclass.qclass,
        "name":                wclass.name,
        "institution":         wclass.institution,
        "email":               wclass.email,
        "class_password":      wclass.password,
        "supervisor_password": wclass.supervisor.password,
        "expiration":          wclass.lang,
        "limit":               wclass.limit,
        "level":               wclass.level,
        'lms_url':             wclass_db.lms.url,
        'wims_url':            wclass_db.wims.url,
    }
    
    root = os.path.join(settings.MAIL_ROOT, wclass.lang)
    tpath = os.path.join(root, "title.txt")
    bpath = os.path.join(root, "body.txt")
    if not (os.path.isfile(tpath) and os.path.isfile(bpath)):
        root = os.path.join(settings.MAIL_ROOT, "en")
        tpath = os.path.join(root, "title.txt")
        bpath = os.path.join(root, "body.txt")
    
    with open(tpath) as t, open(bpath) as b:
        title = t.read().format(**params)
        body = b.read().format(**params)
    
    return title.rstrip(), body



def get_or_create_class(lms: LMS, wims_srv: WIMS, wapi: wimsapi.WimsAPI,
                        parameters: Dict[str, Any]) -> Tuple[WimsClass, wimsapi.Class]:
    """Get the WIMS' class database and wimsapi.Class instances, create them if they does not
    exists.

    Raises:
        - exceptions.PermissionDenied if the class does not exists and none of the roles in
            the LTI request's parameters is in ROLES_ALLOWED_CREATE_WIMS_CLASS.
        - wimsapi.WimsAPIError if the WIMS' server denied a request.
        - requests.RequestException if the WIMS server could not be joined.

    Returns a tuple (wclass_db, wclass) where wclas_db is an instance of models.WimsClass and
    wclass an instance of wimsapi.Class."""
    try:
        wclass_db = WimsClass.objects.get(wims=wims_srv, lms=lms,
                                          lms_guid=parameters['context_id'])
        
        try:
            wclass = wimsapi.Class.get(wapi.url, wapi.ident, wapi.passwd, wclass_db.qclass,
                                       wims_srv.rclass)
        except wimsapi.WimsAPIError as e:
            if "not existing" in str(e):  # Class was deleted on the WIMS server
                logger.info(("Deleting class (id : %d - wims id : %s - lms id : %s) as it was"
                             "deleted from the WIMS server.")
                            % (wclass_db.id, str(wclass_db.qclass), str(wclass_db.lms_guid)))
                wclass_db.delete()
                raise WimsClass.DoesNotExist
            raise  # Unknown error (pragma: no cover)
    
    except WimsClass.DoesNotExist:
        role = Role.parse_role_lti(parameters["roles"])
        if not is_teacher(role):
            logger.warning(str(role))
            msg = ("You must have at least one of these roles to create a Wims class: %s. Your "
                   "roles: %s")
            msg %= (str([r.value for r in settings.ROLES_ALLOWED_CREATE_WIMS_CLASS]),
                    str([r.value for r in role]))
            raise PermissionDenied(msg)
        
        wclass = create_class(wims_srv, parameters)
        wclass.save(wapi.url, wapi.ident, wapi.passwd, timeout=settings.WIMSAPI_TIMEOUT)
        wclass_db = WimsClass.objects.create(
            lms=lms, lms_guid=parameters["context_id"],
            wims=wims_srv, qclass=wclass.qclass, name=wclass.name
        )
        logger.info("New class created (id : %d - wims id : %s - lms id : %s)"
                    % (wclass_db.id, str(wclass.qclass), str(wclass_db.lms_guid)))
        WimsUser.objects.create(wclass=wclass_db, quser="supervisor")
        logger.info("New user created (wims id : supervisor - lms id : None) in class %d"
                    % wclass_db.id)
        
        try:
            title, body = generate_mail(wclass_db, wclass)
            send_mail(
                title,
                body,
                settings.SERVER_EMAIL,
                [wclass.supervisor.email],
            )
        except Exception:
            logger.exception("An exception occurred while sending email:")
    
    return wclass_db, wclass

    

def wims_username(firstname: str, lastname: str) -> str:
    """Create a valid login identifier for WIMS, taking care of translating
    accented characters to their ASCII counterpart.
    
    Replace some other character with underscores."""
    src = "áàâäçéèêëíìîïóòôöúùûü'- "
    dst = "aaaaceeeeiiiioooouuuu___"
    translation = str.maketrans(src, dst)
    quser = (firstname[0] + lastname).lower()[:22]
    return quser.translate(translation)



def create_user(parameters: Dict[str, Any]) -> wimsapi.User:
    """Create an instance of wimsapi.User with the given LTI request's parameters."""
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
    lastname = parameters['lis_person_name_family']
    firstname = parameters['lis_person_name_given']
    mail = parameters["lis_person_contact_email_primary"]
    quser = wims_username(firstname, lastname)
    
    return wimsapi.User(quser, lastname, firstname, password, mail,
                        regnum=parameters["user_id"])



def get_or_create_user(wclass_db: WimsClass, wclass: wimsapi.Class, parameters: Dict[str, Any]
                       ) -> Tuple[WimsUser, wimsapi.User]:
    """Get the WIMS' user database and wimsapi.User instances, create them if they does not
    exists.

    If at least one of the roles in the LTI request's parameters is in
    ROLES_ALLOWED_CREATE_WIMS_CLASS, the user will be connected as supervisor.

    Raises:
        - wimsapi.WimsAPIError if the WIMS' server denied a request.
        - requests.RequestException if the WIMS server could not be joined.

    Returns a tuple (user_db, user) where user_db is an instance of models.WimsUser and
    user an instance of wimsapi.User."""
    try:
        role = Role.parse_role_lti(parameters["roles"])
        if is_teacher(role):
            user_db = WimsUser.objects.get(lms_guid=None, wclass=wclass_db)
        else:
            user_db = WimsUser.objects.get(lms_guid=parameters['user_id'], wclass=wclass_db)
        user = wimsapi.User.get(wclass, user_db.quser)
    except WimsUser.DoesNotExist:
        user = create_user(parameters)
        
        i = 0
        while True:
            try:
                wclass.additem(user)
                break
            except wimsapi.WimsAPIError as e:
                # Raised if an user with the same quser already exists,
                # in this case, keep trying by appending integer to quser (jdoe, jdoe1,
                # jdoe2, ...), stopping after 100 tries.
                
                # Can also be raised if an error occured while communicating with the
                # WIMS server, hence the following test.
                if "user already exists" not in str(e) or i >= 100:  # pragma: no cover
                    raise
                
                if i:
                    user.quser = user.quser[:-len(str(i))]
                i += 1
                user.quser += str(i)
        
        user_db = WimsUser.objects.create(
            lms_guid=parameters["user_id"], wclass=wclass_db, quser=user.quser
        )
        logger.info("New user created (wims id: %s - lms id : %s) in class %d"
                    % (user.quser, str(user_db.lms_guid), wclass_db.id))
    
    return user_db, user



def get_sheet(wclass_db: WimsClass, wclass: wimsapi.Class, qsheet: int, parameters: Dict[str, Any]
              ) -> Tuple[WimsSheet, wimsapi.Sheet]:
    """Get the WIMS' sheet database and wimsapi.Sheet instances, create them if they does not
    exists.

    Raises:
        - wimsapi.WimsAPIError if the WIMS' server denied a request.
        - requests.RequestException if the WIMS server could not be joined.

    Returns a tuple (sheet_db, sheet) where sheet_db is an instance of models.WimsSheet and
    sheet an instance of wimsapi.Sheet."""
    
    sheet = wclass.getitem(qsheet, Sheet)
    try:
        sheet_db = WimsSheet.objects.get(wclass=wclass_db, qsheet=str(qsheet))
        sheet_db.lms_guid = parameters["resource_link_id"]
        sheet_db.save()
    except WimsSheet.DoesNotExist:
        sheet_db = WimsSheet.objects.create(
            lms_guid=parameters["resource_link_id"],
            wclass=wclass_db, qsheet=str(qsheet)
        )
        logger.info("New sheet created (wims id: %s - lms id : %s) in class %d"
                    % (str(qsheet), str(sheet_db.lms_guid), wclass_db.id))
    
    return sheet_db, sheet



def get_exam(wclass_db: WimsClass, wclass: wimsapi.Class, qexam: int, parameters: Dict[str, Any]
             ) -> Tuple[WimsExam, wimsapi.Exam]:
    """Get the WIMS' exam database and wimsapi.Exam instances, create them if they does not
    exists.

    Raises:
        - wimsapi.WimsAPIError if the WIMS' server denied a request.
        - requests.RequestException if the WIMS server could not be joined.

    Returns a tuple (exam_db, exam) where exam_db is an instance of models.WimsExam and
    exam an instance of wimsapi.Exam."""
    
    exam = wclass.getitem(qexam, Exam)
    try:
        exam_db = WimsExam.objects.get(wclass=wclass_db, qexam=str(qexam))
        exam_db.lms_guid = parameters["resource_link_id"]
        exam_db.save()
    except WimsExam.DoesNotExist:
        exam_db = WimsExam.objects.create(
            lms_guid=parameters["resource_link_id"],
            wclass=wclass_db, qexam=str(qexam)
        )
        logger.info("New exam created (wims id: %s - lms id : %s) in class %d"
                    % (str(qexam), str(exam_db.lms_guid), wclass_db.id))
    
    return exam_db, exam
