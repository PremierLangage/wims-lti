import os

from django.test import Client, TestCase
from django.urls import reverse
from wimsapi import Class, Sheet, User

from api.models import LMS, WIMS, WimsClass


# URL to the WIMS server used for tests, the server must recogned ident 'myself' and passwd 'toto'
WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi"
PASSWORD = "password"



class ViewTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
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
        
        s1 = Sheet("Sheet1", "Desc1")
        s2 = Sheet("Sheet2", "Desc2")
        c2.additem(s1)
        c2.additem(s2)
    
    
    def test_get_wims(self):
        r = Client().get(reverse("api:wims", args=[999]))
        self.assertEqual(r.status_code, 200)
        self.assertJSONEqual(
            str(r.content, encoding='utf8'),
            {'content': []}
        )
        
        r = Client().get(reverse("api:wims", args=[self.lms1.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertJSONEqual(
            str(r.content, encoding='utf8'),
            {'content': []}
        )
        
        r = Client().get(reverse("api:wims", args=[self.lms2.pk]))
        self.assertJSONEqual(
            str(r.content, encoding='utf8'),
            {
                'content': [
                    {
                        "pk":      self.wims1.pk,
                        "name":    self.wims1.name,
                        "url":     self.wims1.url,
                        "lti_url": ("http://testserver"
                                    + reverse("lti:wims_class", args=[self.wims1.pk]))
                    }
                ]
            }
        )
        
        r = Client().get(reverse("api:wims", args=[self.lms3.pk]))
        self.assertJSONEqual(
            str(r.content, encoding='utf8'),
            {
                'content': [
                    {
                        "pk":      self.wims1.pk,
                        "name":    self.wims1.name,
                        "url":     self.wims1.url,
                        "lti_url": ("http://testserver"
                                    + reverse("lti:wims_class", args=[self.wims1.pk]))
                    },
                    {
                        "pk":      self.wims2.pk,
                        "name":    self.wims2.name,
                        "url":     self.wims2.url,
                        "lti_url": ("http://testserver"
                                    + reverse("lti:wims_class", args=[self.wims2.pk]))
                    }
                ]
            }
        )
    
    
    def test_get_classes(self):
        r = Client().get(reverse("api:classes", args=[self.wims1.pk]))
        
        self.assertJSONEqual(
            str(r.content, encoding='utf8'),
            {'content': []}
        )
        
        r = Client().get(reverse("api:classes", args=[self.wims2.pk]))
        self.assertJSONEqual(
            str(r.content, encoding='utf8'),
            {'content': [self.class1.serialize(), self.class2.serialize()]}
        )
    
    
    def test_get_activities(self):
        r = Client().get(
            reverse("api:activities", args=[self.class1.pk]),
            {"password": PASSWORD}
        )
        self.assertJSONEqual(
            str(r.content, encoding='utf8'),
            {'content': []}
        )
        
        r = Client().get(
            reverse("api:activities", args=[self.class2.pk]),
            {"password": PASSWORD}
        )
        self.assertJSONEqual(
            str(r.content, encoding='utf8'),
            {
                'content': [
                    {'id': '1', 'title': 'Sheet1', "lti_url": 'http://testserver/lti/2/1/'},
                    {'id': '2', 'title': 'Sheet2', "lti_url": 'http://testserver/lti/2/2/'},
                ]
            }
        )
        
        r = Client().get(
            reverse("api:activities", args=[self.class2.pk]),
            {}
        )
        self.assertContains(r, "Missing parameter: 'password'", status_code=400)
        
        r = Client().get(
            reverse("api:activities", args=[self.class2.pk]),
            {"password": "wrong"}
        )
        self.assertContains(r, "Invalid password", status_code=403)
        
        r = Client().get(
            reverse("api:activities", args=[self.class2.pk]),
            {"password": "wrong"}
        )
        self.assertContains(r, "Invalid password", status_code=403)
        
        c = WimsClass.objects.create(lms=self.lms3, wims=self.wims1, lms_uuid=3, qclass="test",
                                     name="test")
        r = Client().get(
            reverse("api:activities", args=[c.pk]),
            {"password": "wrong"}
        )
        self.assertContains(r, "Could not join the WIMS server '%s'" % self.wims1.url,
                            status_code=504)
