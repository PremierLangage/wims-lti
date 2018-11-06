
from django.conf import settings
from django.http import HttpResponseBadRequest



def check_parameters(param):
    """Check that mandatory parameters are present (either by LTI
    specification or because required by this app)."""
    
    if not all([param[i] is not None for i in settings.LTI_MANDATORY]):
        missing = [i for i in settings.LTI_MANDATORY if param[i] is None]
        raise HttpResponseBadRequest("LTI request is invalid, missing parameter(s): "
                                     + str(missing))
    
    if not all([param[i] is not None for i in settings.WIMSLTI_MANDATORY]):
        missing = [i for i in settings.WIMSLTI_MANDATORY if param[i] is None]
        raise HttpResponseBadRequest("LTI request is invalid, WIMS LTI require parameter(s): "
                                     + str(missing))



def parse_parameters(param):
    """Returns the a dictionnary of the LTI request parameters,
    replacing missing parameters with None."""
    
    return {
        'context_id': param.get('context_id'),
        'context_label': param.get('context_label'),
        'context_title': param.get('context_title'),
        'context_type': param.get('context_type'),
        'custom_canvas_account_id': param.get('custom_canvas_account_id'),
        'custom_canvas_account_sis_id': param.get('custom_canvas_account_sis_id'),
        'custom_canvas_api_domain': param.get('custom_canvas_api_domain'),
        'custom_canvas_course_id': param.get('custom_canvas_course_id'),
        'custom_canvas_enrollment_state': param.get('custom_canvas_enrollment_state'),
        'custom_canvas_membership_roles': param.get('custom_canvas_membership_roles','').split(','),
        'custom_canvas_user_id': param.get('custom_canvas_user_id'),
        'custom_canvas_user_login_id': param.get('custom_canvas_user_login_id'),
        'launch_presentation_css_url': param.get('launch_presentation_css_url'),
        'launch_presentation_document_target': param.get('launch_presentation_document_target'),
        'launch_presentation_height': param.get('launch_presentation_height'),
        'launch_presentation_locale': param.get('launch_presentation_locale'),
        'launch_presentation_return_url': param.get('launch_presentation_return_url'),
        'launch_presentation_width': param.get('launch_presentation_width'),
        'lis_course_offering_sourcedid': param.get('lis_course_offering_sourcedid'),
        'lis_outcome_service_url': param.get('lis_outcome_service_url'),
        'lis_result_sourcedid': param.get('lis_result_sourcedid'),
        'lis_person_contact_email_primary': param.get('lis_person_contact_email_primary'),
        'lis_person_name_family': param.get('lis_person_name_family'),
        'lis_person_name_full': param.get('lis_person_name_full'),
        'lis_person_name_given': param.get('lis_person_name_given'),
        'lis_person_sourcedid': param.get('lis_person_sourcedid'),
        'lti_message_type': param.get('lti_message_type'),
        'oauth_consumer_key': param.get('oauth_consumer_key'),
        'resource_link_description': param.get('resource_link_description'),
        'resource_link_id': param.get('resource_link_id'),
        'resource_link_title': param.get('resource_link_title'),
        'roles': param.get('roles', '').split(','),
        'selection_directive': param.get('selection_directive'),
        'tool_consumer_info_product_family_code': param.get('tool_consumer_info_product_family_code'),
        'tool_consumer_info_version': param.get('tool_consumer_info_version'),
        'tool_consumer_instance_contact_email': param.get('tool_consumer_instance_contact_email'),
        'tool_consumer_instance_description': param.get('tool_consumer_instance_description'),
        'tool_consumer_instance_guid': param.get('tool_consumer_instance_guid'),
        'tool_consumer_instance_name': param.get('tool_consumer_instance_name'),
        'tool_consumer_instance_url': param.get('tool_consumer_instance_url'),
        'user_id': param.get('user_id'),
        'user_image' : param.get('user_image'),
    }