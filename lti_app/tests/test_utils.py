# -*- coding: utf-8 -*-
#
#  test_utils.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import time
import traceback
from datetime import date, datetime, timedelta

import oauth2
import oauthlib.oauth1.rfc5849.signature as oauth_signature
from django.conf import settings
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from django.urls import reverse
from wimsapi import Class, Exam, Sheet, User, WimsAPI

from lti_app import utils
from lti_app.exceptions import BadRequestException
from lti_app.models import LMS, WIMS, WimsClass, WimsUser
from lti_app.tests.utils import KEY, SECRET, WIMS_URL, TEST_SERVER
from lti_app.utils import parse_parameters



class IsValidRequestTestCase(TestCase):
    
    def test_is_valid_request_ok(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
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
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key="provider1", secret="secret1")
        
        try:
            utils.is_valid_request(request)
        except Exception:
            self.fail(traceback.format_exc())
    
    
    def test_is_valid_request_wrong_lti_message_type(self):
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
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        with self.assertRaises(BadRequestException) as r:
            utils.is_valid_request(request)
        self.assertEqual("LTI request is invalid, parameter 'lti_message_type' must be equal to "
                         "'basic-lti-launch-request'",
                         str(r.exception))
    
    
    def test_is_valid_request_invalid_key(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
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
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret2", None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        with self.assertRaises(PermissionDenied):
            utils.is_valid_request(request)
    
    
    def test_is_valid_request_unknown_consumer(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
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
            'oauth_consumer_key':                 'unknown',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret2", None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        with self.assertRaisesMessage(PermissionDenied, "Unknown consumer key: 'unknown'"):
            utils.is_valid_request(request)
    
    
    def test_is_valid_request_timestamp_outdated(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
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
            'oauth_timestamp':                    str(int(time.time()) - 2000),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        
        uri = oauth_signature.base_string_uri(
            TEST_SERVER + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.signature_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, SECRET, None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM", key="provider1", secret="secret1")
        with self.assertRaises(PermissionDenied):
            utils.is_valid_request(request)



class CheckParametersTestCase(TestCase):
    
    def test_check_parameters_ok(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
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
            'oauth_signature':                    oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        params = utils.parse_parameters(params)
        
        self.assertIsNone(utils.check_parameters(params))
    
    
    def test_check_parameters_custom_custom(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
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
            'oauth_signature':                    oauth2.generate_nonce(),
            'roles':                              "Learner",
            'custom_custom_class_name':           "Custom",
            'custom_custom_class_institution':    "Custom",
        }
        
        with self.assertRaises(BadRequestException) as e:
            utils.parse_parameters(params)
        self.assertIn('custom_custom_class_name', str(e.exception))
        self.assertIn('custom_custom_class_institution', str(e.exception))
    
    
    def test_check_parameters_missing_lti_mandatory(self):
        params = {
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
            'oauth_signature':                    oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        params = utils.parse_parameters(params)
        
        with self.assertRaises(BadRequestException) as r:
            utils.check_parameters(params)
        self.assertEqual("LTI request is invalid, missing parameter(s): ['lti_message_type']",
                         str(r.exception))
    
    
    def test_check_parameters_wimslti_mandatory(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-FR',
            'resource_link_id':                   'X',
            'context_id':                         'X',
            'context_title':                      "A title",
            'lis_person_contact_email_primary':   'X',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'X',
            'tool_consumer_instance_guid':        'elearning.u-pem.fr',
            'oauth_consumer_key':                 KEY,
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'oauth_signature':                    oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        params = utils.parse_parameters(params)
        
        with self.assertRaises(BadRequestException) as r:
            utils.check_parameters(params)
        self.assertEqual("LTI request is invalid, WIMS LTI require parameter(s): ['user_id']",
                         str(r.exception))



class GetOrCreateClassTestCase(TestCase):
    
    def tearDown(self):
        """Delete created class with known ID."""
        api = WimsAPI(WIMS_URL, "myself", "toto")
        api.delclass(60000, "myclass")
        api.delclass(60001, "myclass")
        api.delclass(60002, "myclass")
        api.delclass(60003, "myclass")
        api.delclass(60004, "myclass")
        api.delclass(60005, "myclass")
        api.delclass(60006, "myclass")
        super().tearDown()
    
    
    def test_get_or_create_class_create_ok(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        api = WimsAPI(WIMS_URL, "myself", "toto")
        wclass_db, wclass = utils.get_or_create_class(lms, wims, api, params)
        
        self.assertEqual(wclass_db.lms, lms)
        self.assertEqual(wclass_db.lms_guid, "77777")
        self.assertEqual(wclass_db.wims, wims)
        
        self.assertEqual(wclass.email, params["lis_person_contact_email_primary"])
        self.assertEqual(wclass.name, params["context_title"])
        self.assertEqual(wclass.institution, params["tool_consumer_instance_description"])
        self.assertEqual(wclass.lang, params["launch_presentation_locale"][:2])
        self.assertEqual(wclass.supervisor.email, params["lis_person_contact_email_primary"])
    
    
    def test_get_or_create_class_create_expiration(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM", expiration=timedelta(days=400),
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        api = WimsAPI(WIMS_URL, "myself", "toto")
        utils.get_or_create_class(lms, wims, api, params)  # Create and save
        wclass_db, wclass = utils.get_or_create_class(lms, wims, api, params)  # Retrieve from WIMS
        
        self.assertEqual(wclass.expiration,
                         datetime.strftime((date.today() + wims.expiration), "%Y%m%d"))
    
    
    def test_get_or_create_class_create_limit(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM", class_limit=123,
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        api = WimsAPI(WIMS_URL, "myself", "toto")
        utils.get_or_create_class(lms, wims, api, params)  # Create and save
        wclass_db, wclass = utils.get_or_create_class(lms, wims, api, params)  # Retrieve from WIMS
        
        self.assertEqual(wclass.limit, wims.class_limit)
    
    
    def test_get_or_create_class_create_custom_parameters(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
            'custom_class_name':                  "Custom class name",
            'custom_class_institution':           "Custom class institution",
            'custom_class_email':                 "custom@class.mail",
            'custom_class_lang':                  "it",
            'custom_class_expiration':            (date.today()
                                                   + timedelta(days=31)).strftime("%Y%m%d"),
            'custom_class_limit':                 "250",
            'custom_class_level':                 "E1",
            'custom_supervisor_lastname':         "Custom lastname",
            'custom_supervisor_firstname':        "Custom firstname",
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        api = WimsAPI(WIMS_URL, "myself", "toto")
        utils.get_or_create_class(lms, wims, api, params)
        _, wclass = utils.get_or_create_class(lms, wims, api, params)  # Retrieve from WIMS
        
        self.assertEqual(wclass.name, params["custom_class_name"])
        self.assertEqual(wclass.institution, params["custom_class_institution"])
        self.assertEqual(wclass.email, params["custom_class_email"])
        self.assertEqual(wclass.lang, params["custom_class_lang"])
        self.assertEqual(wclass.expiration, params["custom_class_expiration"])
        self.assertEqual(wclass.limit, int(params["custom_class_limit"]))
        self.assertEqual(wclass.level, params["custom_class_level"])
        self.assertEqual(wclass.supervisor.lastname, params["custom_supervisor_lastname"])
        self.assertEqual(wclass.supervisor.firstname, params["custom_supervisor_firstname"])
    
    
    def test_get_or_create_create_class_forbidden(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'UPEM',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "None",
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        api = WimsAPI(WIMS_URL, "myself", "toto")
        
        with self.assertRaises(PermissionDenied) as r:
            utils.get_or_create_class(lms, wims, api, params)
        self.assertIn("['None']", str(r.exception))
        self.assertIn(str([r.value for r in settings.ROLES_ALLOWED_CREATE_WIMS_CLASS]),
                      str(r.exception))
    
    
    def test_get_or_create_class_get_ok(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'UPEM',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        wclass_db1 = WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims,
                                              qclass="60001", name="test1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        
        wclass1 = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password",
                        supervisor, lang="fr", qclass=wclass_db1.qclass)
        wclass1.save(WIMS_URL, "myself", "toto")
        api = WimsAPI(WIMS_URL, "myself", "toto")
        
        wclass_db2, wclass2 = utils.get_or_create_class(lms, wims, api, params)
        
        self.assertEqual(wclass_db1.lms_guid, wclass_db2.lms_guid)
        self.assertEqual(wclass_db1.wims, wclass_db2.wims)
        self.assertEqual(wclass_db1.qclass, wclass_db2.qclass)
        
        self.assertEqual(wclass1.email, wclass2.email)
        self.assertEqual(wclass1.name, wclass2.name)
        self.assertEqual(wclass1.institution, wclass2.institution)
        self.assertEqual(wclass1.lang, wclass2.lang)
        self.assertEqual(wclass1.qclass, wclass2.qclass)
        self.assertEqual(wclass1.supervisor.email, wclass2.supervisor.email)
        
        wclass1.delete()
    
    
    def test_get_or_create_class_get_deleted_from_wims(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'UPEM',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        wclass_db1 = WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims,
                                              qclass="60001", name="test1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        
        wclass1 = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password",
                        supervisor, lang="fr", qclass=wclass_db1.qclass)
        wclass1.save(WIMS_URL, "myself", "toto")
        api = WimsAPI(WIMS_URL, "myself", "toto")
        wclass1.delete()
        
        wclass_db2, wclass2 = utils.get_or_create_class(lms, wims, api, params)
        
        self.assertEqual(wclass_db1.lms_guid, wclass_db2.lms_guid)
        self.assertEqual(wclass_db1.wims, wclass_db2.wims)
        self.assertNotEqual(wclass_db1.qclass, wclass_db2.qclass)
        
        self.assertEqual(wclass1.email, wclass2.email)
        self.assertEqual(wclass1.name, wclass2.name)
        self.assertEqual(wclass1.institution, wclass2.institution)
        self.assertEqual(wclass1.lang, wclass2.lang)
        self.assertNotEqual(wclass1.qclass, wclass2.qclass)
        self.assertEqual(wclass1.supervisor.email, wclass2.supervisor.email)
        
        wclass2.delete()
    
    
    def test_get_or_create_class_create_mail(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "Title",
            'user_id':                            'X',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'X',
            'lis_person_name_given':              'X',
            'tool_consumer_instance_description': 'UPEM',
            'tool_consumer_instance_guid':        "elearning.upem.fr",
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[
                                                      0].value,
        }
        params = utils.parse_parameters(params)
        
        wims = WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key=KEY, secret=SECRET)
        api = WimsAPI(WIMS_URL, "myself", "toto")
        wclass_db, wclass = utils.get_or_create_class(lms, wims, api, params)
        
        self.assertIn(wclass.name, mail.outbox[0].body)
        self.assertIn(wclass.qclass, mail.outbox[0].body)
        self.assertIn(wclass.password, mail.outbox[0].body)
        self.assertIn(wclass.supervisor.password, mail.outbox[0].body)



class GetOrCreateUserTestCase(TestCase):
    
    def test_wims_username(self):
        self.assertEqual("jdoe", utils.wims_username("Jhon", "Doe"))
        
        # Strip to 22 first character
        self.assertEqual(
            "jhaveasurnamewithwayto",
            utils.wims_username("Jhon", "HaveASurnameWithWayTooMuchCharacter")
        )
        
        # Translate accented letter to their ASCII counterpart
        self.assertEqual("jlefevre", utils.wims_username("Jean", "Lefèvre"))
        self.assertEqual(
            "jaaaceeeiiiooouuuu", utils.wims_username("Jean", "àâäçéêëíìïóòôúùûü")
        )
    
    
    def test_get_or_create_user_create_ok(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "None",
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        wclass_db = WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims,
                                             qclass="60002", name="test1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password",
                       supervisor, lang="fr", qclass=wclass_db.qclass)
        wclass.save(WIMS_URL, "myself", "toto")
        
        user_db, user = utils.get_or_create_user(wclass_db, wclass, params)
        
        self.assertEqual(user_db.lms_guid, params["user_id"])
        self.assertEqual(user_db.wclass, wclass_db)
        self.assertEqual(user_db.quser, "jdoe")
        
        self.assertEqual(user.quser, "jdoe")
        self.assertEqual(user.lastname, params["lis_person_name_family"])
        self.assertEqual(user.firstname, params["lis_person_name_given"])
        self.assertEqual(user.email, params["lis_person_contact_email_primary"])
    
    
    def test_get_or_create_user_create_username_already_exists(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "None",
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        wclass_db = WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims,
                                             qclass="60003", name="test1")
        WimsUser.objects.create(lms_guid='66', wclass=wclass_db, quser="jdoe")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password",
                       supervisor, lang="fr", qclass=wclass_db.qclass)
        wclass.save(WIMS_URL, "myself", "toto")
        
        lastname = params['lis_person_name_family']
        firstname = params['lis_person_name_given']
        mail = params["lis_person_contact_email_primary"]
        quser = (firstname[0] + lastname).lower()
        wclass.additem(User(quser, lastname, firstname, "password", mail))
        
        user_db, user = utils.get_or_create_user(wclass_db, wclass, params)
        
        self.assertEqual(user_db.lms_guid, params["user_id"])
        self.assertEqual(user_db.wclass, wclass_db)
        self.assertEqual(user_db.quser, "jdoe1")
        
        self.assertEqual(user.quser, "jdoe1")
        self.assertEqual(user.lastname, params["lis_person_name_family"])
        self.assertEqual(user.firstname, params["lis_person_name_given"])
        self.assertEqual(user.email, params["lis_person_contact_email_primary"])
    
    
    def test_get_or_create_user_create_username_already_exists2(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "None",
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        wclass_db = WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims,
                                             qclass="60004", name="test1")
        WimsUser.objects.create(lms_guid='66', wclass=wclass_db, quser="jdoe")
        WimsUser.objects.create(lms_guid='67', wclass=wclass_db, quser="jdoe1")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password",
                       supervisor, lang="fr", qclass=wclass_db.qclass)
        wclass.save(WIMS_URL, "myself", "toto")
        
        lastname = params['lis_person_name_family']
        firstname = params['lis_person_name_given']
        mail = params["lis_person_contact_email_primary"]
        quser = (firstname[0] + lastname).lower()
        wclass.additem(User(quser, lastname, firstname, "password", mail))
        wclass.additem(User(quser + "1", lastname, firstname, "password", mail))
        
        user_db, user = utils.get_or_create_user(wclass_db, wclass, params)
        
        self.assertEqual(user_db.lms_guid, params["user_id"])
        self.assertEqual(user_db.wclass, wclass_db)
        self.assertEqual(user_db.quser, "jdoe2")
        
        self.assertEqual(user.quser, "jdoe2")
        self.assertEqual(user.lastname, params["lis_person_name_family"])
        self.assertEqual(user.firstname, params["lis_person_name_given"])
        self.assertEqual(user.email, params["lis_person_contact_email_primary"])
    
    
    def test_get_or_create_user_get(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "None",
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        wclass_db = WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims,
                                             qclass="60005", name="test1")
        user_db1 = WimsUser.objects.create(lms_guid='77', wclass=wclass_db, quser="jdoe")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password",
                       supervisor, lang="fr", qclass=wclass_db.qclass)
        wclass.save(WIMS_URL, "myself", "toto")
        
        lastname = params['lis_person_name_family']
        firstname = params['lis_person_name_given']
        mail = params["lis_person_contact_email_primary"]
        quser = (firstname[0] + lastname).lower()
        user1 = User(quser, lastname, firstname, "password", mail)
        wclass.additem(user1)
        
        user_db2, user2 = utils.get_or_create_user(wclass_db, wclass, params)
        
        self.assertEqual(user_db1.lms_guid, user_db2.lms_guid)
        self.assertEqual(user_db1.wclass, user_db2.wclass)
        self.assertEqual(user_db1.quser, user_db2.quser)
        
        self.assertEqual(user1.quser, user2.quser)
        self.assertEqual(user1.lastname, user2.lastname)
        self.assertEqual(user1.firstname, user2.firstname)
        self.assertEqual(user1.email, user2.email)
    
    
    def test_get_or_create_user_get_supervisor(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   'X',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Jean',
            'lis_person_name_given':              'Dupont',
            'tool_consumer_instance_description': 'UPEM',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        wclass_db = WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims,
                                             qclass="60006", name="test1")
        WimsUser.objects.create(lms_guid=None, wclass=wclass_db, quser="supervisor")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password",
                       supervisor, lang="fr", qclass=wclass_db.qclass)
        wclass.save(WIMS_URL, "myself", "toto")
        
        user_db, user = utils.get_or_create_user(wclass_db, wclass, params)
        
        self.assertEqual(user_db.lms_guid, None)
        self.assertEqual(user_db.wclass, wclass_db)
        self.assertEqual(user_db.quser, "supervisor")
        
        self.assertEqual(user.quser, "supervisor")
        self.assertEqual(user.lastname, "Supervisor")
        self.assertEqual(user.firstname, "")
        self.assertEqual(user.email, params["lis_person_contact_email_primary"])



class GetSheetTestCase(TestCase):
    
    def test_get_sheet_ok(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   '789',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "None",
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM", ident="X", passwd="X", rclass="myclass")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password",
                       supervisor, lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        wclass_db = WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims,
                                             qclass=wclass.qclass, name="test1")
        wclass.additem(Sheet("Titre", "Description"))
        activity, sheet = utils.get_sheet(wclass_db, wclass, 1, params)
        
        self.assertEqual(activity.qsheet, "1")
        self.assertEqual(activity.wclass, wclass_db)
        self.assertEqual(activity.lms_guid, params["resource_link_id"])
        activity2, sheet2 = utils.get_sheet(wclass_db, wclass, 1, params)
        
        self.assertEqual(activity2.qsheet, activity.qsheet)
        self.assertEqual(activity2.wclass, activity.wclass)
        self.assertEqual(activity2.lms_guid, activity.lms_guid)



class GetExamTestCase(TestCase):
    
    def test_get_exam_ok(self):
        params = {
            'lti_message_type':                   'basic-lti-launch-request',
            'lti_version':                        'LTI-1p0',
            'launch_presentation_locale':         'fr-BE',
            'resource_link_id':                   '789',
            'context_id':                         '77777',
            'context_title':                      "A title",
            'user_id':                            '77',
            'lis_person_contact_email_primary':   'test@email.com',
            'lis_person_name_family':             'Doe',
            'lis_person_name_given':              'Jhon',
            'tool_consumer_instance_description': 'UPEM',
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "None",
        }
        params = parse_parameters(params)
        
        wims = WIMS.objects.create(url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM", ident="X", passwd="X", rclass="myclass")
        supervisor = User("supervisor", "Supervisor", "", "password", "test@email.com")
        wclass = Class(wims.rclass, "A title", "UPEM", "test@email.com", "password",
                       supervisor, lang="fr")
        wclass.save(WIMS_URL, "myself", "toto")
        lms = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                 name="Moodle UPEM", key="provider1", secret="secret1")
        wclass_db = WimsClass.objects.create(lms=lms, lms_guid="77777", wims=wims,
                                             qclass=wclass.qclass, name="test1")
        wclass.additem(Exam("Titre", "Description"))
        activity, exam = utils.get_exam(wclass_db, wclass, 1, params)
        
        self.assertEqual(activity.qexam, "1")
        self.assertEqual(activity.wclass, wclass_db)
        self.assertEqual(activity.lms_guid, params["resource_link_id"])
        activity2, exam2 = utils.get_exam(wclass_db, wclass, 1, params)
        
        self.assertEqual(activity2.qexam, activity.qexam)
        self.assertEqual(activity2.wclass, activity.wclass)
        self.assertEqual(activity2.lms_guid, activity.lms_guid)
