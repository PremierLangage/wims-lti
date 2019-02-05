import os

import oauth2
import oauthlib.oauth1.rfc5849.signature as oauth_signature
from django.conf import settings
from django.http import Http404
from django.shortcuts import reverse
from django.test import Client, RequestFactory, TestCase, override_settings

from wims import views
from wims.models import LMS, WIMS
from wims.templatetags.markdown import markdown


# URL to the WIMS server used for tests, the server must recogned ident 'myself' and passwd 'toto'
WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi"

FAKE_CREDENTIALS = {
    'provider1': 'secret1',
}



@override_settings(LTI_OAUTH_CREDENTIALS=FAKE_CREDENTIALS)
class RedirectToWimsTestCase(TestCase):
    
    def test_redirect_to_wims_ok(self):
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
        uri = oauth_signature.normalize_base_string_uri("https://testserver/dns/dns/")
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("wims:from_dns", args=["dns"]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(dns="wims.upem.fr", url=WIMS_URL,
                                   name="WIMS UPEM",
                                   ident="myself", passwd="toto", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        r = views.redirect_to_wims(request, wims)
        
        self.assertIn(WIMS_URL, r.url)
    
    
    def test_redirect_to_wims_unknown_lms(self):
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
            'roles':                              settings.ROLES_ALLOWED_CREATE_WIMS_CLASS[0].value,
        }
        
        norm_params = oauth_signature.normalize_parameters([(k, v) for k, v in params.items()])
        # Last 'dns' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri("https://testserver/dns/dns/")
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("wims:from_dns", args=["dns"]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(dns="wims.upem.fr", url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="X", passwd="X", rclass="myclass")
        
        with self.assertRaisesMessage(Http404, "No LMS found with uuid '%s'"
                                               % params["tool_consumer_instance_guid"]):
            views.redirect_to_wims(request, wims)
    
    
    def test_redirect_to_wims_wrong_ident_passwd(self):
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
        uri = oauth_signature.normalize_base_string_uri("https://testserver/dns/dns/")
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        
        request = RequestFactory().post(reverse("wims:from_dns", args=["dns"]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(dns="wims.upem.fr", url="https://wims.u-pem.fr/",
                                   name="WIMS UPEM",
                                   ident="wrong", passwd="wrong", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        
        r = views.redirect_to_wims(request, wims)
        self.assertContains(r, "Identification Failure : bad login/pwd", status_code=421)



@override_settings(LTI_OAUTH_CREDENTIALS=FAKE_CREDENTIALS)
class FromDNSTestCase(TestCase):
    
    def test_from_dns_ok(self):
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
        uri = oauth_signature.normalize_base_string_uri("https://testserver/dns/dns/")
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("wims:from_dns", args=["dns"]), secure=True)
        request.POST = params
        
        WIMS.objects.create(dns="dns", url=WIMS_URL,
                            name="WIMS UPEM",
                            ident="myself", passwd="toto", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        r = views.from_dns(request, "dns")
        self.assertIn(WIMS_URL, r.url)
    
    
    def test_from_dns_invalid_method(self):
        r = Client().patch(reverse("wims:from_dns", args=["im.a.dns"]))
        self.assertContains(r, "405 Method Not Allowed: 'PATCH'", status_code=405)
    
    
    def test_from_dns_invalid_method_get(self):
        r = Client().get(reverse("wims:from_dns", args=["im.a.dns"]))
        self.assertContains(r, "405 Method Not Allowed: 'GET'. Did you forget trailing '/' ?",
                            status_code=405)
    
    
    def test_from_dns_invalid_lti(self):
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
        request = RequestFactory().post(reverse("wims:from_dns", args=["dns"]), secure=True)
        request.POST = params
        
        WIMS.objects.create(dns="dns", url=WIMS_URL,
                            name="WIMS UPEM",
                            ident="myself", passwd="toto", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        r = views.from_dns(request, "dns")
        self.assertContains(r, "LTI request is invalid, missing parameter(s): ['oauth_signature']",
                            status_code=400)
    
    
    def test_from_dns_unknown_dns(self):
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
        uri = oauth_signature.normalize_base_string_uri("https://testserver/dns/dns/")
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("wims:from_dns", args=["dns"]), secure=True)
        request.POST = params
        
        with self.assertRaisesMessage(Http404, "Unknown WIMS server 'unknown'"):
            views.from_dns(request, "unknown")



@override_settings(LTI_OAUTH_CREDENTIALS=FAKE_CREDENTIALS)
class FromIDTestCase(TestCase):
    
    def test_from_id_ok(self):
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
        uri = oauth_signature.normalize_base_string_uri("https://testserver/dns/dns/")
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("wims:from_dns", args=["dns"]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(dns="dns", url=WIMS_URL,
                                   name="WIMS UPEM",
                                   ident="myself", passwd="toto", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        r = views.from_id(request, wims.pk)
        self.assertIn(WIMS_URL, r.url)
    
    
    def test_from_id_invalid_method(self):
        r = Client().patch(reverse("wims:from_id", args=[1]))
        self.assertContains(r, "405 Method Not Allowed: 'PATCH'", status_code=405)
    
    
    def test_from_id_invalid_method_get(self):
        r = Client().get(reverse("wims:from_id", args=[1]))
        self.assertContains(r, "405 Method Not Allowed: 'GET'. Did you forget trailing '/' ?",
                            status_code=405)
    
    
    def test_from_id_invalid_lti(self):
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
        request = RequestFactory().post(reverse("wims:from_id", args=[1]), secure=True)
        request.POST = params
        
        wims = WIMS.objects.create(dns="dns", url=WIMS_URL,
                                   name="WIMS UPEM",
                                   ident="myself", passwd="toto", rclass="myclass")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        r = views.from_id(request, wims.pk)
        self.assertContains(r, "LTI request is invalid, missing parameter(s): ['oauth_signature']",
                            status_code=400)
    
    
    def test_from_id_unknown_dns(self):
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
        # Last 'id' is the arg use in request factory
        uri = oauth_signature.normalize_base_string_uri("https://testserver/id/1/")
        base_string = oauth_signature.construct_base_string("POST", uri, norm_params)
        
        params['oauth_signature'] = oauth_signature.sign_hmac_sha1(base_string, "secret1", None)
        request = RequestFactory().post(reverse("wims:from_id", args=[1]), secure=True)
        request.POST = params
        
        with self.assertRaisesMessage(Http404, "Unknown WIMS server of id '99999'"):
            views.from_id(request, 99999)



class ListTestCase(TestCase):
    
    def test_list_nothing(self):
        response = Client().get(reverse("wims:ls"))
        
        self.assertContains(response, "No LMS found")
        self.assertContains(response, "No WIMS server found")
    
    
    def test_list(self):
        WIMS.objects.create(dns="wims.upem.fr", url="https://wims.u-pem.fr/", name="WIMS UPEM",
                            ident="X", passwd="X", rclass="X")
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        response = Client().get(reverse("wims:ls"))
        
        self.assertContains(response,
                            '<td class="w-25">Moodle UPEM</td>'
                            '<td>https://elearning.u-pem.fr/</td>',
                            html=True)
        self.assertContains(response,
                            '<td class="w-25">WIMS UPEM</td>'
                            '<td>https://wims.u-pem.fr/</td>'
                            '<td>http://testserver/dns/wims.upem.fr/</td>',
                            html=True)



class AboutTestCase(TestCase):
    
    def test_about_default(self):
        with open("README.md") as f:
            content = f.read()
        response = Client().get(reverse("wims:about"))
        
        self.assertContains(response, markdown(content))
    
    
    def test_about_en(self):
        with open("README.md") as f:
            content = f.read()
        response = Client().get(reverse("wims:about"))
        
        self.assertContains(response, markdown(content))
    
    
    def test_about_lang_ok(self):
        with open("translation/README_fr.md") as f:
            content = f.read()
        response = Client().get(reverse("wims:about", args=["fr"]))
        
        self.assertContains(response, markdown(content))
    
    
    def test_about_lang_unknown(self):
        response = Client().get(reverse("wims:about", args=["unknown"]))
        self.assertContains(response, "Unknown language : &#39;unknown&#39;", status_code=404)
