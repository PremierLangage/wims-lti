from django.test import TestCase

from lti_app import utils



class UtilsTestCase(TestCase):
    
    def test_check_parameters_ok(self):
        params = {
            'lti_message_type': 'basic-lti-launch-request',
            'lti_version': 'LTI-1p0',
            'launch_presentation_locale': 'fr-FR',
            'resource_link_id': 'X',
            'context_id': 'X',
            'context_title': "A title",
            'user_id': 'X',
            'lis_person_contact_email_primary': 'X',
            'lis_person_name_family': 'X',
            'lis_person_name_given': 'X',
            'oauth_consumer_key': 'provider1',
            'roles': "Learner"
        }
        params = utils.parse_parameters(params)
        self.assertIsNone(utils.check_parameters(params))
    
    
    def test_check_parameters_missing_lti_mandatory(self):
        params = {
            'lti_version': 'LTI-1p0',
            'launch_presentation_locale': 'fr-FR',
            'resource_link_id': 'X',
            'context_id': 'X',
            'context_title': "A title",
            'user_id': 'X',
            'lis_person_contact_email_primary': 'X',
            'lis_person_name_family': 'X',
            'lis_person_name_given': 'X',
            'oauth_consumer_key': 'provider1',
            'roles': "Learner"
        }
        params = utils.parse_parameters(params)
        self.assertIsNotNone(utils.check_parameters(params))
    
    
    def test_check_parameters_wimslti_mandatory(self):
        params = {
            'lti_message_type': 'basic-lti-launch-request',
            'lti_version': 'LTI-1p0',
            'launch_presentation_locale': 'fr-FR',
            'resource_link_id': 'X',
            'context_id': 'X',
            'context_title': "A title",
            'lis_person_contact_email_primary': 'X',
            'lis_person_name_family': 'X',
            'lis_person_name_given': 'X',
            'oauth_consumer_key': 'provider1',
            'roles': "Learner"
        }
        params = utils.parse_parameters(params)
        self.assertIsNotNone(utils.check_parameters(params))
