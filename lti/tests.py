import uuid
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings


ROLES = {
    "Administrator"   : "urn:lti:role:ims/lis/Administrator",
    "Observer"        : "urn:lti:role:ims/lis/Observer",
    "Learner"         : "urn:lti:role:ims/lis/Learner",
    "Instructor"      : "urn:lti:role:ims/lis/Instructor",
    "ContentDeveloper": "urn:lti:role:ims/lis/ContentDeveloper",
}

REQUEST_LTI_1P1 = {
    'lti_message_type'          : 'basic-lti-launch-request',
    'lti_version'               : 'LTI-1p0',
    'launch_presentation_locale': 'fr-FR',
    'resource_link_id'          : None,
}

FAKE_CREDENTIALS = {
    'provider1': 'secret1',
    'provider2': 'secret2',
}



@override_settings(LTI_OAUTH_CREDENTIALS=FAKE_CREDENTIALS)
class LTITestCase(TestCase):
    
    @patch('lti.middleware.logger')
    @patch('lti.backends.logger')
    def test_wrong_key(self, backends_logger, middleware_logger):
        params = {
            **REQUEST_LTI_1P1,
            **{
                'resource_link_id'     : str(uuid.uuid4()),
                'oauth_consumer_key'   : 'wrong',
                'oauth_consumer_secret': 'wrong',
            }
        }
        c = Client()
        response = c.post('/', data=params, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('LTI authentication failed',
                         tuple(middleware_logger.warning.call_args)[0][0])
        self.assertEqual('Beginning authentication process',
                         tuple(backends_logger.info.call_args)[0][0])
        self.assertEqual(
                ('LTI Authentification aborted: '
                 + 'Could not get a secret for key wrong'),
                tuple(backends_logger.warning.call_args)[0][0])
        self.assertFalse(User.objects.all())
    
    
    @patch('lti.middleware.logger')
    @patch('lti.backends.logger')
    def test_right_key(self, backends_logger, middleware_logger):
        params = {
            **REQUEST_LTI_1P1,
            **{
                'resource_link_id'     : str(uuid.uuid4()),
                'oauth_consumer_key'   : 'provider1',
                'oauth_consumer_secret': 'secret1',
            }
        }
        c = Client()
        response = c.post('/', data=dict(params), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('LTI authentication failed',
                         tuple(middleware_logger.warning.call_args)[0][0])
        self.assertEqual('Beginning authentication process',
                         tuple(backends_logger.info.call_args)[0][0])
        self.assertEqual(
                ("Missing on of the argument [lis_person_contact_email_primary, "
                 + "lis_person_name_given, lis_person_name_family, user_id] in the LTI"
                 + "request."),
                tuple(backends_logger.warning.call_args)[0][0])
        self.assertFalse(User.objects.all())
