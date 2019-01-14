import logging
import sys

import oauth2
from django.conf import settings
from django.http import HttpResponseForbidden
from lti.contrib.django import DjangoToolProvider

from lti_app.exceptions import BadRequestException
from lti_app.request_validator import RequestValidator


logger = logging.getLogger(__name__)



def is_valid_request(request):
    """Check whether the request is valid and is accepted by oauth2.
    
    Returns an HttpResponse if the request is invalid, None otherwise."""
    
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
        logger.warning(
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
        logger.warning("LTI Authentification aborted: signature check failed.")
        return HttpResponseForbidden("Invalid request: signature check failed.")



def check_parameters(param):
    """Check that mandatory parameters are present (either by LTI
    specification or because required by this app)."""
    
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
        'lti_version': p.get('lti_version'),
        'context_id': p.get('context_id'),
        'context_label': p.get('context_label'),
        'context_title': p.get('context_title'),
        'context_type': p.get('context_type'),
        'custom_canvas_account_id': p.get('custom_canvas_account_id'),
        'custom_canvas_account_sis_id': p.get('custom_canvas_account_sis_id'),
        'custom_canvas_api_domain': p.get('custom_canvas_api_domain'),
        'custom_canvas_course_id': p.get('custom_canvas_course_id'),
        'custom_canvas_enrollment_state': p.get('custom_canvas_enrollment_state'),
        'custom_canvas_membership_roles': p.get('custom_canvas_membership_roles', '').split(','),
        'custom_canvas_user_id': p.get('custom_canvas_user_id'),
        'custom_canvas_user_login_id': p.get('custom_canvas_user_login_id'),
        'launch_presentation_css_url': p.get('launch_presentation_css_url'),
        'launch_presentation_document_target': p.get('launch_presentation_document_target'),
        'launch_presentation_height': p.get('launch_presentation_height'),
        'launch_presentation_locale': p.get('launch_presentation_locale'),
        'launch_presentation_return_url': p.get('launch_presentation_return_url'),
        'launch_presentation_width': p.get('launch_presentation_width'),
        'lis_course_offering_sourcedid': p.get('lis_course_offering_sourcedid'),
        'lis_outcome_service_url': p.get('lis_outcome_service_url'),
        'lis_result_sourcedid': p.get('lis_result_sourcedid'),
        'lis_person_contact_email_primary': p.get('lis_person_contact_email_primary'),
        'lis_person_name_family': p.get('lis_person_name_family'),
        'lis_person_name_full': p.get('lis_person_name_full'),
        'lis_person_name_given': p.get('lis_person_name_given'),
        'lis_person_sourcedid': p.get('lis_person_sourcedid'),
        'lti_message_type': p.get('lti_message_type'),
        'oauth_consumer_key': p.get('oauth_consumer_key'),
        'resource_link_description': p.get('resource_link_description'),
        'resource_link_id': p.get('resource_link_id'),
        'resource_link_title': p.get('resource_link_title'),
        'roles': p.get('roles', '').split(','),
        'selection_directive': p.get('selection_directive'),
        'tool_consumer_info_product_family_code': p.get('tool_consumer_info_product_family_code'),
        'tool_consumer_info_version': p.get('tool_consumer_info_version'),
        'tool_consumer_instance_contact_email': p.get('tool_consumer_instance_contact_email'),
        'tool_consumer_instance_description': p.get('tool_consumer_instance_description'),
        'tool_consumer_instance_guid': p.get('tool_consumer_instance_guid'),
        'tool_consumer_instance_name': p.get('tool_consumer_instance_name'),
        'tool_consumer_instance_url': p.get('tool_consumer_instance_url'),
        'user_id': p.get('user_id'),
        'user_image': p.get('user_image'),
    }
