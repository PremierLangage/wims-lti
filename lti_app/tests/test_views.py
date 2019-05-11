import os

import oauth2
import oauthlib.oauth1.rfc5849.signature as oauth_signature
from django.conf import settings
from django.http import Http404
from django.shortcuts import reverse
from django.test import Client, RequestFactory, TestCase, override_settings

from api.models import LMS, WIMS
from lti_app import views


# URL to the WIMS server used for tests, the server must recogned ident 'myself' and passwd 'toto'
WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi"

FAKE_CREDENTIALS = {
    'provider1': 'secret1',
}



@override_settings(LTI_OAUTH_CREDENTIALS=FAKE_CREDENTIALS)
class WimsClassTestCase(TestCase):
    
    def test_wims_class_ok(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        # Last 'dns' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        r = views.wims_class(request, 1)
        self.assertIn(WIMS_URL, r.url)
    
    
    def test_wims_class_invalid_method(self):
        r = Client().patch(reverse("lti:wims_class", args=[1]))
        self.assertContains(r, "405 Method Not Allowed: 'PATCH'", status_code=405)
    
    
    def test_wims_class_invalid_method_get(self):
        r = Client().get(reverse("lti:wims_class", args=[1]))
        self.assertContains(r, "405 Method Not Allowed: 'GET'. Did you forget trailing '/' ?",
                            status_code=405)
    
    
    def test_wims_class_invalid_lti(self):
        params = {
            'lti_message_type':                   'wrong',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         'X',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'X',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'X',
            'tool_consumer_instance_guid':        'elearning.u-pem.fr',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL,
                            name="WIMS UPEM",
                            ident="myself", passwd="toto", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        r = views.wims_class(request, 1)
        self.assertContains(r, "LTI request is invalid, missing parameter(s): ['oauth_signature']",
                            status_code=400)
    
    
    def test_wims_class_unknown_wims(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        # Last 'dns' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        with self.assertRaisesMessage(Http404, "Unknown WIMS server of id '999999'"):
            views.wims_class(request, 999999)
    
    
    def test_wims_class_unknown_lms(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "unknown.fr",
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        # Last 'dns' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        
        with self.assertRaisesMessage(Http404, "No LMS found with uuid '%s'"
                                               % params["tool_consumer_instance_guid"]):
            views.wims_class(request, wims.pk)
    
    
    def test_wims_class_wrong_ident_passwd(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/", name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        
        r = views.wims_class(request, wims.pk)
        self.assertContains(r, "Identification Failure : bad login/pwd", status_code=502)
