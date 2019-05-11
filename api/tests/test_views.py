from django.test import TestCase, override_settings, Client
from django.urls import reverse

from api.models import LMS



class getWimsTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        LMS.objects.create(uuid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                           name="Moodle UPEM")
        LMS.objects.create(uuid="elearning.test.fr", url="https://elearning.test.fr/",
                           name="Moodle Test")

        WIMS.objects.create(url=WIMS_URL, name="WIMS UPEM", ident="myself", passwd="toto",
                            rclass="myclass")
        
    def test_wims_class_ok(self):
        r = Client().get(reverse("api:wims", args=[1]))
