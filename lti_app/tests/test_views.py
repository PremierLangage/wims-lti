import os

import oauth2
import oauthlib.oauth1.rfc5849.signature as oauth_signature
from django.conf import settings
from django.http import Http404
from django.shortcuts import reverse
from django.test import Client, RequestFactory, TestCase
from wimsapi import Class, Sheet, User

from lti_app import views
# URL to the WIMS server used for tests, the server must recogned ident 'myself' and passwd 'toto'
from lti_app.enums import Role
from lti_app.models import LMS, WIMS, WimsClass


WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi"

KEY = 'provider1'
SECRET = 'secret1'
PASSWORD = "password"



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
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
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
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
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
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
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
            'oauth_consumer_key':                 KEY,
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
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="X", passwd="X",
                                   rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
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
            'oauth_consumer_key':                 KEY,
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
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_class(request, wims.pk)
        self.assertContains(r, "Identification Failure : bad login/pwd", status_code=502)
    
    
    def test_wims_class_could_not_join_server(self):
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
            'oauth_consumer_key':                 KEY,
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
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url="https://can.not.join.fr/", name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_class(request, wims.pk)
        self.assertContains(r, "https://can.not.join.fr/", status_code=504)



class WimsActivityTestCase(TestCase):
    
    def test_wims_activity_ok(self):
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
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_uuid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.additem(Sheet("Titre", "Description", sheetmode=1))
        
        r = views.wims_activity(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("sh=1", r.url)
    
    
    def test_wims_activity_class_deleted_from_wims(self):
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
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_uuid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.delete()
        
        r = views.wims_activity(request, 1, 1)
        
        print(r.content)
        self.assertContains(r, "could not be found", status_code=404)
        self.assertContains(r, "https://testserver/lti/1/", status_code=404)
    
    
    def test_wims_class_invalid_method(self):
        r = Client().patch(reverse("lti:wims_activity", args=[1, 1]))
        self.assertContains(r, "405 Method Not Allowed: 'PATCH'", status_code=405)
    
    
    def test_wims_class_invalid_method_get(self):
        r = Client().get(reverse("lti:wims_activity", args=[1, 1]))
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
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        r = views.wims_activity(request, 1, 1)
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
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        with self.assertRaisesMessage(Http404, "Unknown WIMS server of id '999999'"):
            views.wims_activity(request, 999999, 1)
    
    
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
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="X", passwd="X",
                                   rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        with self.assertRaisesMessage(Http404, "No LMS found with uuid '%s'"
                                               % params["tool_consumer_instance_guid"]):
            views.wims_activity(request, wims.pk, 1)
    
    
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
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_activity(request, wims.pk, 1)
        self.assertContains(r, "Identification Failure : bad login/pwd", status_code=502)
    
    
    def test_wims_class_could_not_join_server(self):
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
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url="https://can.not.join.fr/", name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_activity(request, wims.pk, 1)
        self.assertContains(r, "https://can.not.join.fr/", status_code=504)
    
    
    def test_wims_activity_unknown_wimsclass(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         '77778',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key="provider1", secret="secret1")
        
        r = views.wims_activity(request, 1, 1)
        self.assertContains(r, "Could not find class of id '77778'", status_code=404)
    
    
    def test_wims_activity_ok_student(self):
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
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.LEARNER.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_uuid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.additem(Sheet("Titre", "Description", sheetmode=1))
        
        r = views.wims_activity(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("sh=1", r.url)
    
    
    def test_wims_activity_ok_overwrite_sourcedid(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   '7777',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.LEARNER.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_activity", args=[1, 1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_activity", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself",
                                   passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_uuid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.additem(Sheet("Titre", "Description", sheetmode=1))
        
        views.wims_activity(request, 1, 1)
        r = views.wims_activity(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("sh=1", r.url)



class BaseLinksViewTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.lms1 = LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                      name="No WIMS", key="provider1", secret="secret1")
        cls.lms2 = LMS.objects.create(uuid="elearning.test.fr", url="https://elearning.test.fr/",
                                      name="One WIMS", key="provider2", secret="secret1")
        cls.lms3 = LMS.objects.create(uuid="elearning.test.fr", url="https://elearning.test.fr/",
                                      name="Two WIMS", key="provider3", secret="secret1")
        
        cls.wims1 = WIMS.objects.create(url="www.lti_app.com", name="One", ident="myself",
                                        passwd="toto", rclass="myclass")
        cls.wims2 = WIMS.objects.create(url=WIMS_URL, name="Two", ident="myself", passwd="toto",
                                        rclass="myclass")
        
        cls.wims1.allowed_lms.add(cls.lms2)
        cls.wims1.allowed_lms.add(cls.lms3)
        cls.wims2.allowed_lms.add(cls.lms3)
        
        c1 = Class("myclass", "Classe 1", "Institution", "email", PASSWORD,
                   User("supervisor", "First", "Last", PASSWORD))
        c2 = Class("myclass", "Classe 2", "Institution", "email", PASSWORD,
                   User("supervisor", "First", "Last", PASSWORD))
        c1.save(cls.wims2.url, cls.wims2.ident, cls.wims2.passwd)
        c2.save(cls.wims2.url, cls.wims2.ident, cls.wims2.passwd)
        cls.class1 = WimsClass.objects.create(lms=cls.lms3, wims=cls.wims2, lms_uuid=1,
                                              qclass=c1.qclass, name=c1.name)
        cls.class2 = WimsClass.objects.create(lms=cls.lms3, wims=cls.wims2, lms_uuid=2,
                                              qclass=c2.qclass, name=c2.name)
        
        cls.sheet1 = Sheet("Sheet1", "Desc1")
        cls.sheet2 = Sheet("Sheet2", "Desc2")
        c2.additem(cls.sheet1)
        c2.additem(cls.sheet2)



class LMSTestCase(BaseLinksViewTestCase):
    
    def test_lms(self):
        response = self.client.get(reverse("lti:lms"))
        self.assertTemplateUsed(response, 'lti_app/base.html')
        self.assertTemplateUsed(response, 'lti_app/lms.html')
        self.assertContains(response, 'No WIMS')
        self.assertContains(response, 'One WIMS')
        self.assertContains(response, 'Two WIMS')



class WIMSTestCase(BaseLinksViewTestCase):
    
    def test_wims(self):
        response = self.client.get(reverse("lti:wims", args=[self.lms3.pk]))
        self.assertTemplateUsed(response, 'lti_app/base.html')
        self.assertTemplateUsed(response, 'lti_app/wims.html')
        self.assertContains(response, 'One')
        self.assertContains(response, 'Two')
        self.assertContains(response, reverse('lti:wims_class', args=[self.wims1.pk]))



class ClassesTestCase(BaseLinksViewTestCase):
    
    def test_classes(self):
        response = self.client.get(reverse("lti:classes", args=[self.lms3.pk, self.wims2.pk]))
        self.assertTemplateUsed(response, 'lti_app/base.html')
        self.assertTemplateUsed(response, 'lti_app/classes.html')
        self.assertContains(response, 'Classe 1')
        self.assertContains(response, 'Classe 2')



class SheetTestCase(BaseLinksViewTestCase):
    
    def test_sheets(self):
        response = self.client.post(
            reverse("lti:sheets", args=[self.lms3.pk, self.wims2.pk, self.class2.pk]),
            {"password": PASSWORD}
        )
        self.assertContains(response, 'Sheet1')
        self.assertContains(response, 'Sheet2')
        self.assertContains(response,
                            reverse('lti:wims_activity', args=[self.wims2.pk, self.sheet1.qsheet]))
        self.assertContains(response,
                            reverse('lti:wims_activity', args=[self.wims2.pk, self.sheet2.qsheet]))
        self.assertTemplateUsed(response, 'lti_app/base.html')
        self.assertTemplateUsed(response, 'lti_app/activities.html')
    
    
    def test_sheets_class_404(self):
        response = self.client.post(
            reverse("lti:sheets", args=[self.lms3.pk, self.wims2.pk, 99999]),
        )
        self.assertEqual(404, response.status_code)
    
    
    def test_sheets_missing_password(self):
        response = self.client.post(
            reverse("lti:sheets", args=[self.lms3.pk, self.wims2.pk, self.class2.pk]),
        )
        self.assertEqual(400, response.status_code)
    
    
    def test_sheets_invalid_password(self):
        response = self.client.post(
            reverse("lti:sheets", args=[self.lms3.pk, self.wims2.pk, self.class2.pk]),
            {"password": "wrong"},
            follow=True
        )
        
        self.assertTemplateUsed(response, 'lti_app/base.html')
        self.assertTemplateUsed(response, 'lti_app/classes.html')
        self.assertContains(response, "Invalid password")
