# -*- coding: utf-8 -*-
#
#  utils.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging
import secrets
import string
import sys

import oauth2
from django.conf import settings
from django.core.exceptions import PermissionDenied
from lti.contrib.django import DjangoToolProvider
from wimsapi import AdmRawError, Class, User

from wims.enums import Role
from wims.exceptions import BadRequestException
from wims.models import WimsClass, WimsUser
from wims.validator import RequestValidator


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
        if 'test' in sys.argv:
            request_is_valid = True
        else:
            tool_provider = DjangoToolProvider.from_django_request(request=request)
            request_is_valid = tool_provider.is_valid_request(RequestValidator())
    except oauth2.Error:
        logger.exception("error attempting to validate LTI launch with parameters: %s", parameters)
        request_is_valid = False
    
    if not request_is_valid:
        logger.info("LTI Authentification aborted: signature check failed.")
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



def parse_parameters(p):
    """Returns the a dictionnary of the LTI request parameters,
    replacing missing parameters with None."""
    return {
        'lti_version'                           : p.get('lti_version'),
        'context_id'                            : p.get('context_id'),
        'context_label'                         : p.get('context_label'),
        'context_title'                         : p.get('context_title'),
        'context_type'                          : p.get('context_type'),
        'custom_canvas_account_id'              : p.get('custom_canvas_account_id'),
        'custom_canvas_account_sis_id'          : p.get('custom_canvas_account_sis_id'),
        'custom_canvas_api_domain'              : p.get('custom_canvas_api_domain'),
        'custom_canvas_course_id'               : p.get('custom_canvas_course_id'),
        'custom_canvas_enrollment_state'        : p.get('custom_canvas_enrollment_state'),
        'custom_canvas_membership_roles'        : p.get('custom_canvas_membership_roles', ''),
        'custom_canvas_user_id'                 : p.get('custom_canvas_user_id'),
        'custom_canvas_user_login_id'           : p.get('custom_canvas_user_login_id'),
        'launch_presentation_css_url'           : p.get('launch_presentation_css_url'),
        'launch_presentation_document_target'   : p.get('launch_presentation_document_target'),
        'launch_presentation_height'            : p.get('launch_presentation_height'),
        'launch_presentation_locale'            : p.get('launch_presentation_locale'),
        'launch_presentation_return_url'        : p.get('launch_presentation_return_url'),
        'launch_presentation_width'             : p.get('launch_presentation_width'),
        'lis_course_offering_sourcedid'         : p.get('lis_course_offering_sourcedid'),
        'lis_outcome_service_url'               : p.get('lis_outcome_service_url'),
        'lis_result_sourcedid'                  : p.get('lis_result_sourcedid'),
        'lis_person_contact_email_primary'      : p.get('lis_person_contact_email_primary'),
        'lis_person_name_family'                : p.get('lis_person_name_family'),
        'lis_person_name_full'                  : p.get('lis_person_name_full'),
        'lis_person_name_given'                 : p.get('lis_person_name_given'),
        'lis_person_sourcedid'                  : p.get('lis_person_sourcedid'),
        'lti_message_type'                      : p.get('lti_message_type'),
        'oauth_consumer_key'                    : p.get('oauth_consumer_key'),
        'resource_link_description'             : p.get('resource_link_description'),
        'resource_link_id'                      : p.get('resource_link_id'),
        'resource_link_title'                   : p.get('resource_link_title'),
        'roles'                                 : p.get('roles', ''),
        'selection_directive'                   : p.get('selection_directive'),
        'tool_consumer_info_product_family_code': p.get('tool_consumer_info_product_family_code'),
        'tool_consumer_info_version'            : p.get('tool_consumer_info_version'),
        'tool_consumer_instance_contact_email'  : p.get('tool_consumer_instance_contact_email'),
        'tool_consumer_instance_description'    : p.get('tool_consumer_instance_description'),
        'tool_consumer_instance_guid'           : p.get('tool_consumer_instance_guid'),
        'tool_consumer_instance_name'           : p.get('tool_consumer_instance_name'),
        'tool_consumer_instance_url'            : p.get('tool_consumer_instance_url'),
        'user_id'                               : p.get('user_id'),
        'user_image'                            : p.get('user_image'),
    }



def create_class(rclass, parameters):
    mail = parameters["lis_person_contact_email_primary"]
    title = parameters["context_title"]
    institution = parameters["tool_consumer_instance_description"]
    cpassword = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
    upassword = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
    supervisor = User("supervisor", "Moodle", "Moodle", upassword, mail)
    
    return Class(rclass, title, institution, mail, cpassword, supervisor)



def get_or_create_class(lms, wims_srv, api, parameters):
    try:
        wclass_db = WimsClass.objects.get(wims=wims_srv, lms=lms, lms_uuid=parameters['context_id'])
        wclass = Class.get(api.url, api.ident, api.passwd, wclass_db.wims_uuid, wclass_db.rclass)
    
    except WimsClass.DoesNotExist:
        role = Role.parse_role_lti(parameters["roles"])
        if set(role).isdisjoint(settings.ROLES_ALLOWED_CREATE_WIMS_CLASS):
            msg = ("You must have at least one of these roles to create a Wims class: %s. Your "
                   "roles: %s")
            msg %= (str(r.label for r in settings.ROLES_ALLOWED_CREATE_WIMS_CLASS),
                    str(r.label for r in role))
            raise PermissionDenied(msg)
        
        wclass = create_class(wims_srv.rclass, parameters)
        wclass.save(api.url, api.ident, api.passwd)
        wclass_db = WimsClass.objects.create(
                lms=lms, lms_uuid=parameters["tool_consumer_instance_guid"],
                wims=wims_srv, wims_uuid=wclass.qclass
        )
    
    return wclass_db, wclass



def create_user(parameters):
    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
    lastname = parameters['lis_person_name_family']
    firstname = parameters['lis_person_name_given']
    mail = parameters["lis_person_contact_email_primary"]
    quser = firstname[0] + lastname
    role = Role.parse_role_lti(parameters["roles"])
    supervisable = "no" if set(role).isdisjoint(settings.ROLES_ALLOWED_CREATE_WIMS_CLASS) else "yes"
    
    return User(quser, lastname, firstname, password, mail, supervisable=supervisable,
                regnum=parameters["user_id"])



def get_or_create_user(lms, wclass_db, wclass, parameters):
    try:
        user_db = WimsUser.objects.get(lms=lms, lms_uuid=parameters['user_id'], wclass=wclass_db)
        user = User.get(wclass, user_db.quser)
    except WimsUser.DoesNotExist:
        user = create_user(parameters)
        
        i = 0
        while True:
            try:
                user.save(wclass)
                break
            except AdmRawError as e:
                # Raised if an user with an user with the same quser already exists,
                # in this case, keep trying by appending integer to quser (jdoe, jdoe1,
                # jdoe2, ...), stopping after 100 tries.
                
                # Can also be raised if an error occured while communicating with the
                # WIMS server, hence the follow test.
                if "user already exists" not in str(e) or i >= 100:
                    raise
                
                if i:
                    user.quser = user.quser[:-len(str(i))]
                i += 1
                user.quser += str(i)
        
        user_db = WimsUser.objects.create(
                lms=lms, lms_uuid=parameters["tool_consumer_instance_guid"],
                wclass=wclass_db, quser=user.quser
        )
    
    return user_db, user
