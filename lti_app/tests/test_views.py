# -*- coding: utf-8 -*-
#
#  test_views.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#


import oauth2
import oauthlib.oauth1.rfc5849.signature as oauth_signature
from django.conf import settings
from django.http import Http404
from django.shortcuts import reverse
from django.test import Client, RequestFactory, TestCase
from wimsapi import Class, Exam, Sheet, User

from lti_app import views
from lti_app.enums import Role
from lti_app.models import LMS, WIMS, WimsClass
from lti_app.tests.utils import (BaseLinksViewTestCase, KEY, SECRET, TEST_SERVER, WIMS_URL,
                                 untar_archive)



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
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "http://www.outcom.com",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        r = views.wims_class(request, 1)
        self.assertIn(WIMS_URL, r.url)
    
    
    def test_wims_class_invalid_method(self):
        r = Client().patch(reverse("lti:wims_class", args=[1]))
        self.assertContains(r, "405 Method Not Allowed: 'PATCH'", status_code=405)
    
    
    def test_wims_class_invalid_method_get(self):
        r = Client().get(reverse("lti:wims_class", args=[1]))
        self.assertContains(r, "405 Method Not Allowed: 'GET'", status_code=405)
    
    
    def test_wims_class_invalid_lti(self):
        params = {
            'lti_message_type':                   'wrong',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         'X',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "http://www.outcom.com",
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
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
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
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "http://www.outcom.com",
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
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
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
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "http://www.outcom.com",
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
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="X", passwd="X",
                                   rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        with self.assertRaisesMessage(Http404, "No LMS found with guid '%s'"
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
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "http://www.outcom.com",
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
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
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
            'lis_result_sourcedid':               "14821455",
            'lis_outcome_service_url':            "http://www.outcom.com",
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
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url="https://can.not.join.fr/", name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_class(request, wims.pk)
        self.assertContains(r, "https://can.not.join.fr/", status_code=504)



class WimsSheetTestCase(TestCase):
    
    def test_wims_sheet_ok(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_sheet", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.additem(Sheet("Titre", "Description", sheetmode=1))
        
        r = views.wims_sheet(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("sh=1", r.url)
    
    
    def test_wims_sheet_class_deleted_from_wims(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_sheet", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.delete()
        
        r = views.wims_sheet(request, 1, 1)
        
        self.assertContains(r, "could not be found", status_code=404)
        self.assertContains(r, "https://testserver/lti/C1/", status_code=404)
    
    
    def test_wims_class_invalid_method(self):
        r = Client().patch(reverse("lti:wims_sheet", args=[1, 1]))
        self.assertContains(r, "405 Method Not Allowed: 'PATCH'", status_code=405)
    
    
    def test_wims_class_invalid_method_get(self):
        r = Client().get(reverse("lti:wims_sheet", args=[1, 1]))
        self.assertContains(r, "405 Method Not Allowed: 'GET'", status_code=405)
    
    
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
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        r = views.wims_sheet(request, 1, 1)
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
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_sheet", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        with self.assertRaisesMessage(Http404, "Unknown WIMS server of id '999999'"):
            views.wims_sheet(request, 999999, 1)
    
    
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
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_sheet", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="X", passwd="X",
                                   rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        with self.assertRaisesMessage(Http404, "No LMS found with guid '%s'"
                                               % params["tool_consumer_instance_guid"]):
            views.wims_sheet(request, wims.pk, 1)
    
    
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
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_sheet", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_sheet(request, wims.pk, 1)
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
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_sheet", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url="https://can.not.join.fr/", name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_sheet(request, wims.pk, 1)
        self.assertContains(r, "https://can.not.join.fr/", status_code=504)
    
    
    def test_wims_sheet_unknown_wimsclass(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_sheet", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key="provider1", secret="secret1")
        
        r = views.wims_sheet(request, 1, 1)
        self.assertContains(r, "Could not find class of id '77778'", status_code=404)
    
    
    def test_wims_sheet_ok_student(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.LEARNER.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_sheet", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        sheet = Sheet("Titre", "Description", sheetmode=1)
        wclass.additem(sheet)
        r = views.wims_sheet(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("sh=1", r.url)
    
    
    def test_wims_sheet_forbidden(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.LEARNER.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_sheet", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        sheet = Sheet("Titre", "Description")
        wclass.additem(sheet)
        r = views.wims_sheet(request, 1, 1)
        
        self.assertEqual(403, r.status_code)
    
    
    def test_wims_sheet_ok_overwrite_sourcedid(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.LEARNER.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_sheet", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_sheet", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself",
                                   passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.additem(Sheet("Titre", "Description", sheetmode=1))
        
        views.wims_sheet(request, 1, 1)
        r = views.wims_sheet(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("sh=1", r.url)



class WimsExamTestCase(TestCase):
    
    def test_wims_exam_ok(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.STUDENT.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        qclass = untar_archive()
        wclass = Class.get(WIMS_URL, "myself", "toto", qclass, "myclass")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        
        r = views.wims_exam(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("exam=1", r.url)
    
    
    def test_wims_exam_class_deleted_from_wims(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        wclass.delete()
        
        r = views.wims_exam(request, 1, 1)
        
        self.assertContains(r, "could not be found", status_code=404)
        self.assertContains(r, "https://testserver/lti/C1/", status_code=404)
    
    
    def test_wims_class_invalid_method(self):
        r = Client().patch(reverse("lti:wims_exam", args=[1, 1]))
        self.assertContains(r, "405 Method Not Allowed: 'PATCH'", status_code=405)
    
    
    def test_wims_class_invalid_method_get(self):
        r = Client().get(reverse("lti:wims_exam", args=[1, 1]))
        self.assertContains(r, "405 Method Not Allowed: 'GET'", status_code=405)
    
    
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
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        r = views.wims_exam(request, 1, 1)
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
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        with self.assertRaisesMessage(Http404, "Unknown WIMS server of id '999999'"):
            views.wims_exam(request, 999999, 1)
    
    
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
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="X", passwd="X",
                                   rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        with self.assertRaisesMessage(Http404, "No LMS found with guid '%s'"
                                               % params["tool_consumer_instance_guid"]):
            views.wims_exam(request, wims.pk, 1)
    
    
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
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_exam(request, wims.pk, 1)
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
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url="https://can.not.join.fr/", name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key=KEY, secret=SECRET)
        
        r = views.wims_exam(request, wims.pk, 1)
        self.assertContains(r, "https://can.not.join.fr/", status_code=504)
    
    
    def test_wims_exam_unknown_wimsclass(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key="provider1", secret="secret1")
        
        r = views.wims_exam(request, 1, 1)
        self.assertContains(r, "Could not find class of id '77778'", status_code=404)
    
    
    def test_wims_exam_ok_student(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.LEARNER.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        qclass = untar_archive()
        wclass = Class.get(WIMS_URL, "myself", "toto", qclass, "myclass")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        r = views.wims_exam(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("exam=1", r.url)
    
    
    def test_wims_exam_ok_teacher(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.INSTRUCTOR.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        qclass = untar_archive()
        wclass = Class.get(WIMS_URL, "myself", "toto", qclass, "myclass")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        r = views.wims_exam(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("exam=1", r.url)
    
    
    def test_wims_exam_forbidden_student(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.LEARNER.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password", supervisor,
                       lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        exam = Exam("Titre", "Description", exammode=1)
        wclass.additem(exam)
        r = views.wims_exam(request, 1, 1)
        self.assertEqual(403, r.status_code)
    
    
    def test_wims_exam_ok_overwrite_sourcedid(self):
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
            'lis_outcome_service_url':            "http://www.outcom.com",
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              Role.LEARNER.value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_exam", args=[1, 1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_exam", args=[1, 1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself",
                                   passwd="toto",
                                   rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        qclass = untar_archive()
        wclass = Class.get(WIMS_URL, "myself", "toto", qclass, "myclass")
        WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims, qclass=wclass.qclass,
                                 name="test1")
        
        views.wims_exam(request, 1, 1)
        r = views.wims_exam(request, 1, 1)
        
        self.assertIn(WIMS_URL, r.url)
        self.assertIn("exam=1", r.url)



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



class ActivitiesTestCase(BaseLinksViewTestCase):
    
    def test_activities(self):
        response = self.client.get(
            reverse("lti:sheets", args=[self.lms3.pk, self.wims2.pk, self.class2.pk]),
        )
        self.assertContains(response, 'Sheet1')
        self.assertContains(response, 'Sheet2')
        self.assertContains(response,
                            reverse('lti:wims_sheet', args=[self.wims2.pk, self.sheet1.qsheet]))
        self.assertContains(response,
                            reverse('lti:wims_sheet', args=[self.wims2.pk, self.sheet2.qsheet]))
        self.assertContains(response, 'Exam1')
        self.assertContains(response, 'Exam2')
        self.assertContains(response,
                            reverse('lti:wims_exam', args=[self.wims2.pk, self.exam1.qexam]))
        self.assertContains(response,
                            reverse('lti:wims_exam', args=[self.wims2.pk, self.exam2.qexam]))
        self.assertTemplateUsed(response, 'lti_app/base.html')
        self.assertTemplateUsed(response, 'lti_app/activities.html')
    
    
    def test_activities_class_404(self):
        response = self.client.get(
            reverse("lti:sheets", args=[self.lms3.pk, self.wims2.pk, 99999]),
        )
        self.assertEqual(404, response.status_code)
    
    
    def test_activities_class_not_found_on_wims(self):
        w = WimsClass.objects.create(
            lms=self.lms1, lms_guid="1337", wims=self.wims2, qclass="1337", name="test1"
        )
        before = WimsClass.objects.all().count()
        
        response = self.client.get(
            reverse("lti:sheets", args=[self.lms1.pk, self.wims2.pk, w.pk]), follow=True
        )
        
        self.assertTemplateUsed(response, 'lti_app/base.html')
        self.assertTemplateUsed(response, 'lti_app/classes.html')
        self.assertEqual(before - 1, WimsClass.objects.all().count())
