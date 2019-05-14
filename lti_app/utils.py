# -*- coding: utf-8 -*-
#
#  utils.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#
import logging
from xml.etree import ElementTree

import oauth2
import requests
import wimsapi
from django.conf import settings
from django.core.exceptions import PermissionDenied
from lti.contrib.django import DjangoToolProvider

from lti_app.exceptions import BadRequestException
from lti_app.validator import CustomParameterValidator, RequestValidator, validate


logger = logging.getLogger(__name__)



def is_valid_request(request):
    """Check whether the request is valid and is accepted by oauth2.

    Raises:
        - api.exceptions.BadRequestException if the request is invalid.
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

    Raises api.exceptions.BadRequestException if this is not the case."""
    
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



def parse_parameters(p):
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
        'custom_clone_class':                     p.get('custom_clone_class'),
        'custom_supervisor_lastname':             p.get('custom_supervisor_lastname'),
        'custom_supervisor_firstname':            p.get('custom_supervisor_firstname'),
    }

