# -*- coding: utf-8 -*-
#
#  utils.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#
import os

from defusedxml import ElementTree
from django.http import HttpResponse, HttpResponseNotFound



def xml_ok(request):
    """Send the right success repsonse after receiving a grade."""
    root = ElementTree.fromstring(request.body.decode())
    identifier = int(root[0][0][1].text)
    sourcedid = root[1][0][0][0][0].text
    grade = float(root[1][0][0][1][0][1].text)
    
    result_path = os.path.join(os.path.dirname(__file__), "resources/replaceResult.xml")
    with open(result_path) as f:
        response = f.read() % ("success", sourcedid, grade, identifier)
    
    return HttpResponse(response.encode(), content_type="application/xml")


def xml_error_response(request):
    """Send an error response after receiving a grade."""
    root = ElementTree.fromstring(request.body.decode())
    identifier = int(root[0][0][1].text)
    sourcedid = root[1][0][0][0][0].text
    grade = float(root[1][0][0][1][0][1].text)

    result_path = os.path.join(os.path.dirname(__file__), "resources/replaceResult.xml")
    with open(result_path) as f:
        response = f.read() % ("failure", sourcedid, grade, identifier)

    return HttpResponse(response.encode(), content_type="application/xml")



def xml_badly_formatted(request):
    """Send a badly formatted response after receiving a grade."""
    return HttpResponseNotFound()
