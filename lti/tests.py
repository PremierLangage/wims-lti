import uuid

from django.contrib.auth.models import User
from django.test import Client, TestCase


ROLES = {
    "Administrator": "urn:lti:role:ims/lis/Administrator",
    "Observer": "urn:lti:role:ims/lis/Observer",
    "Learner": "urn:lti:role:ims/lis/Learner",
    "Instructor": "urn:lti:role:ims/lis/Instructor",
    "ContentDeveloper": "urn:lti:role:ims/lis/ContentDeveloper",
}

REQUEST_LTI_1P1 = {
    'lti_message_type': 'basic-lti-launch-request',
    'lti_version': 'LTI-1p0',
    'launch_presentation_locale': 'fr-FR',
    'resource_link_id': None,
}

FAKE_CREDENTIALS = {
    'provider1': 'secret1',
    'provider2': 'secret2',
}



class LTITestCase(TestCase):
    
    def test_wrong_key(self):
        params = {
            **REQUEST_LTI_1P1,
            **{
                'resource_link_id': str(uuid.uuid4()),
                'oauth_consumer_key': 'wrong',
                'oauth_consumer_secret': 'wrong',
            }
        }
        c = Client()
        response = c.post('/', data=params, follow=True)
        self.assertEqual(response.status_code, 200)
    
    
    def test_right_key(self):
        params = {
            **REQUEST_LTI_1P1,
            **{
                'resource_link_id': str(uuid.uuid4()),
                'oauth_consumer_key': 'provider1',
                'oauth_consumer_secret': 'secret1',
            }
        }
        c = Client()
        response = c.post('/', data=dict(params), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.all())
