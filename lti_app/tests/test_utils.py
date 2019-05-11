import time
import traceback

import oauth2
import oauthlib.oauth1.rfc5849.signature as oauth_signature
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from lti_app import utils
from lti_app.exceptions import BadRequestException


FAKE_CREDENTIALS = {
    'provider1': 'secret1',
}



@override_settings(LTI_OAUTH_CREDENTIALS=FAKE_CREDENTIALS)
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
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        # Last 'dns' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
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
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        # Last 'dns' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        with self.assertRaises(BadRequestException) as r:
            utils.is_valid_request(request)
        self.assertEqual("LTI request is invalid, parameter 'lti_message_type' must be equal to "
                         "'basic-lti-launch-request'",
                         str(r.exception))
    
    
    @override_settings(LTI_OAUTH_CREDENTIALS=False)
    def test_is_valid_request_no_lti_oauth_credentials(self):
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
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        # Last 'dns' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        with self.assertRaises(BadRequestException) as r:
            utils.is_valid_request(request)
        self.assertEqual("Missing LTI_OAUTH_CREDENTIALS in settings.", str(r.exception))
    
    
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
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(oauth2.generate_timestamp()),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        # Last 'dns' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
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
        # Last 'dns' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret2", None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
        with self.assertRaises(BadRequestException) as r:
            utils.is_valid_request(request)
        self.assertEqual("Could not get a secret for key 'unknown'", str(r.exception))
    
    
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
            'oauth_consumer_key':                 'provider1',
            'oauth_signature_method':             'HMAC-SHA1',
            'oauth_timestamp':                    str(int(time.time()) - 2000),
            'oauth_nonce':                        oauth2.generate_nonce(),
            'roles':                              "Learner"
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        # Last 'dns' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri(
            "https://testserver" + reverse("lti:wims_class", args=[1]))
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("lti:wims_class", args=[1]), secure=True)
        request.POST = params
        
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
            'oauth_consumer_key':                 'provider1',
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
            'oauth_consumer_key':                 'provider1',
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
            'oauth_consumer_key':                 'provider1',
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
            'oauth_consumer_key':                 'provider1',
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
