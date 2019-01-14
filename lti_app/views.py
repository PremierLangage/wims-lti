import logging

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from lti_app.exceptions import BadRequestException
from lti_app.utils import check_parameters, is_valid_request, parse_parameters


logger = logging.getLogger(__name__)


@csrf_exempt
def toWims(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"], "405 Method Not Allowed")
	
    logger.info("Request received from '%s'" % request.META['HTTP_REFERER'])
    
    parameters = parse_parameters(request.POST)
    try:
        check_parameters(parameters)
        is_valid_request(request)
    except BadRequestException as e:
        logger.info(str(e))
        return HttpResponseBadRequest("400:" + str(e))
    
    email = parameters["lis_person_contact_email_primary"]
    first_name = parameters["lis_person_name_given"]
    last_name = parameters["lis_person_name_family"]
    user_id = parameters["user_id"]
    role = parameters["roles"]
    username = (first_name[0].lower() + last_name.lower())
    
    return HttpResponse(
        "OK<br>mail: %s<br>first_name: %s<br>lastname: %s<br>user_id: %s<br>username: %s<br>roles: %s" % (email, first_name, last_name, user_id, username, str(role)))
