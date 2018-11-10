import logging

from django.http import HttpResponse
from django.views.decorators.http import require_POST

from lti.request_validator import is_valid_request
from lti.utils import check_parameters, parse_parameters, is_valid_request


logger = logging.getLogger(__name__)



@require_POST
def toWims(request):
    parameters = parse_parameters(request.POST)
    
    response = check_parameters(parameters)
    if response is not None:
        return response
    
    logger.info("Request received from '%s'" % request.META['HTTP_REFERER'])
    
    response = is_valid_request(parameters)
    if response is not None:
        return response
    
    email = parameters["lis_person_contact_email_primary"]
    first_name = parameters["lis_person_name_given"]
    last_name = parameters["lis_person_name_family"]
    user_id = parameters["user_id"]
    username = (first_name[0].lower() + last_name.lower())
    
    return HttpResponse()
