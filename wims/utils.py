# -*- coding: utf-8 -*-
#
#  utils.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging
import random
import string
from datetime import datetime
from string import ascii_letters, digits

import oauth2
import wimsapi
from django.conf import settings
from django.core.exceptions import PermissionDenied
from lti.contrib.django import DjangoToolProvider

from wims.enums import Role
from wims.exceptions import BadRequestException
from wims.models import WimsClass, WimsUser
from wims.validator import CustomParameterValidator, RequestValidator, validate


logger = logging.getLogger(__name__)



def is_valid_request(request):
    """Check whether the request is valid and is accepted by oauth2.
    
    Raises:
        - wims.exceptions.BadRequestException if the request is invalid.
        - django.core.exceptions.PermissionDenied if signature check failed."""
    parameters = parse_parameters(request.POST)
    
    if parameters['lti_message_type'] != 'basic-lti-launch-request':
        raise BadRequestException("LTI request is invalid, parameter 'lti_message_type' "
                                  "must be equal to 'basic-lti-launch-request'")
    
    if not settings.LTI_OAUTH_CREDENTIALS:
        logger.error("LTI Authentification aborted: "
                     "Missing LTI_OAUTH_CREDENTIALS in settings")
        raise BadRequestException("Missing LTI_OAUTH_CREDENTIALS in settings.")
    
    request_key = parameters['oauth_consumer_key']
    secret = settings.LTI_OAUTH_CREDENTIALS.get(request_key)
    if secret is None:
        logger.info(
            "LTI Authentification aborted: Could not get a secret for key '%s'" % request_key)
        raise BadRequestException("Could not get a secret for key '%s'" % request_key)
    
    try:
        tool_provider = DjangoToolProvider.from_django_request(request=request)
        request_is_valid = tool_provider.is_valid_request(RequestValidator())
    except oauth2.Error as e:  # pragma: no cover
        logger.warning("Oauth authentication failed : %s" % str(e))
        request_is_valid = False
    
    if not request_is_valid:
        logger.info("LTI Authentification aborted: signature check failed with parameters : %s",
                    parameters)
        raise PermissionDenied("Invalid request: signature check failed.")



def check_parameters(param):
    """Check that mandatory parameters are present (either by LTI
    specification or required by this app)
    
    Raises wims.exceptions.BadRequestException if this is not the case."""
    
    if not all([param[i] is not None for i in settings.LTI_MANDATORY]):
        missing = [i for i in settings.LTI_MANDATORY if param[i] is None]
        raise BadRequestException("LTI request is invalid, missing parameter(s): "
                                  + str(missing))
    
    if not all([param[i] is not None for i in settings.WIMSLTI_MANDATORY]):
        missing = [i for i in settings.WIMSLTI_MANDATORY if param[i] is None]
        raise BadRequestException("LTI request is invalid, WIMS LTI require parameter(s): "
                                  + str(missing))



def check_custom_parameters(params):
    """Checks that custom parameters, if given, are properly formatted.
    
    Raises wims.exceptions.BadRequestException if this is not the case."""
    validate(
        CustomParameterValidator.email_validator, params['custom_class_email'],
        "Invalid parameter 'custom_class_email' (%s): invalid email" % params['custom_class_email']
    )
    validate(
        CustomParameterValidator.email_validator, params['custom_supervisor_email'],
        ("Invalid parameter 'custom_supervisor_email' (%s): invalid email"
         % params['custom_supervisor_email'])
    )
    validate(
        CustomParameterValidator.username_validator, params['custom_supervisor_username'],
        (("Invalid parameter 'custom_supervisor_username' (%s): Username can only contain "
          "alphanumeric characters and underscores ('_') and cannot start with a number.")
         % params['custom_supervisor_email'])
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



def lti_request_is_valid(request):
    """Check that the LTI request is valid.
    Raises :
        - wims.exceptions.BadRequestException if LTI request is invalid.
        - PermissioNDenied if signature check failed.
    """
    parameters = parse_parameters(request.POST)
    logger.info("Request received from '%s'" % request.META.get('HTTP_REFERER', "Unknown"))
    check_parameters(parameters)
    check_custom_parameters(parameters)
    is_valid_request(request)



def parse_parameters(p):
    """Returns the a dictionnary of the LTI request parameters,
    replacing missing parameters with None."""
    
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
        'custom_clone_class':                     p.get('custom_clone_class'),
        'custom_supervisor_username':             p.get('custom_supervisor_username'),
        'custom_supervisor_lastname':             p.get('custom_supervisor_lastname'),
        'custom_supervisor_firstname':            p.get('custom_supervisor_firstname'),
        'custom_supervisor_email':                p.get('custom_supervisor_email'),
    }



def create_supervisor(params):
    """Create an instance of wimapi.User corresponding to the class' supervisor with the given LTI
    request's parameters."""
    supervisor = {
        "quser":     params["custom_supervisor_username"] or "supervisor",
        "lastname":  (params['custom_supervisor_lastname']
                      or ("" if params['custom_supervisor_firstname'] else "Supervisor")),
        "firstname": params['custom_supervisor_firstname'] or "",
        "password":  ''.join(random.choice(ascii_letters + digits) for _ in range(20)),
        "email":     (params["custom_supervisor_email"]
                      or params["lis_person_contact_email_primary"]),
    }
    return wimsapi.User(**supervisor)



def create_class(wclass_db, params):
    """Create an instance of wimsapi.Class with the given LTI request's parameters and wclass_db."""
    wclass = {
        "name":        params["custom_class_name"] or params["context_title"],
        "institution": (params["custom_class_institution"]
                        or params["tool_consumer_instance_description"]),
        "email":       params["custom_class_email"] or params["lis_person_contact_email_primary"],
        "lang":        params["custom_class_lang"] or params["launch_presentation_locale"][:2],
        "expiration":  (params["custom_class_expiration"]
                        or (datetime.now() + wclass_db.expiration).strftime("%Y%m%d")),
        "limit":       params["custom_class_limit"] or wclass_db.class_limit,
        "level":       params["custom_class_level"] or "H4",
        "css":         params["custom_class_css"] or "",
        "password":    ''.join(random.choice(ascii_letters + digits) for _ in range(20)),
        "supervisor":  create_supervisor(params),
        "rclass":      wclass_db.rclass,
    }
    
    return wimsapi.Class(**wclass)



def get_or_create_class(lms, wims_srv, api, parameters):
    """Get the WIMS' class database and wimsapi.Class instances, create them if they does not
    exists.
    
    Raises:
        - exceptions.PermissionDenied if the class does not exists and none of the roles in
        the LTI
              request's parameters is in ROLES_ALLOWED_CREATE_WIMS_CLASS.
        - wimsapi.AdmRawError if the WIMS' server denied a request or could not be joined.
    
    Returns a tuple (wclass_db, wclass) where wclas_db is an instance of models.WimsClass and
    wclass
    an instance of wimsapi.Class."""
    try:
        wclass_db = WimsClass.objects.get(wims=wims_srv, lms=lms,
                                          lms_uuid=parameters['context_id'])
        wclass = wimsapi.Class.get(api.url, api.ident, api.passwd, wclass_db.wims_uuid,
                                   wims_srv.rclass)
    
    except WimsClass.DoesNotExist:
        role = Role.parse_role_lti(parameters["roles"])
        if set(role).isdisjoint(settings.ROLES_ALLOWED_CREATE_WIMS_CLASS):
            logger.warning(str(role))
            msg = ("You must have at least one of these roles to create a Wims class: %s. Your "
                   "roles: %s")
            msg %= (str([r.value for r in settings.ROLES_ALLOWED_CREATE_WIMS_CLASS]),
                    str([r.value for r in role]))
            raise PermissionDenied(msg)
        
        wclass = create_class(wims_srv, parameters)
        wclass.save(api.url, api.ident, api.passwd)
        wclass_db = WimsClass.objects.create(
            lms=lms, lms_uuid=parameters["context_id"],
            wims=wims_srv, wims_uuid=wclass.qclass
        )
        WimsUser.objects.create(lms=lms, wclass=wclass_db, quser="supervisor")
    
    return wclass_db, wclass



def create_user(parameters):
    """Create an instance of wimsapi.User with the given LTI request's parameters."""
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
    lastname = parameters['lis_person_name_family']
    firstname = parameters['lis_person_name_given']
    mail = parameters["lis_person_contact_email_primary"]
    quser = (firstname[0] + lastname).lower()
    
    return wimsapi.User(quser, lastname, firstname, password, mail,
                        regnum=parameters["user_id"])



def get_or_create_user(lms, wclass_db, wclass, parameters):
    """Get the WIMS' user database and wimsapi.User instances, create them if they does not
    exists.
    
    If at least one of the roles in the LTI request's parameters is in
    ROLES_ALLOWED_CREATE_WIMS_CLASS, the user will be connected as supervisor.
    
    Raises:
        - wimsapi.AdmRawError if the WIMS' server denied a request or could not be joined.

    Returns a tuple (user_db, user) where user_db is an instance of models.WimsUser and
    user an instance of wimsapi.User."""
    try:
        role = Role.parse_role_lti(parameters["roles"])
        if not set(role).isdisjoint(settings.ROLES_ALLOWED_CREATE_WIMS_CLASS):
            user_db = WimsUser.objects.get(lms=lms, lms_uuid=None, wclass=wclass_db)
        else:
            user_db = WimsUser.objects.get(lms=lms, lms_uuid=parameters['user_id'],
                                           wclass=wclass_db)
        user = wimsapi.User.get(wclass, user_db.quser)
    except WimsUser.DoesNotExist:
        user = create_user(parameters)
        
        i = 0
        while True:
            try:
                wclass.additem(user)
                break
            except wimsapi.AdmRawError as e:
                # Raised if an user with an user with the same quser already exists,
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
            lms=lms, lms_uuid=parameters["user_id"],
            wclass=wclass_db, quser=user.quser
        )
    
    return user_db, user
