# -*- coding: utf-8 -*-
#
#  utils.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import os
import subprocess

from django.conf import settings
from django.test import Client, LiveServerTestCase, TestCase
from django.urls import reverse
from wimsapi import Class, Exam, Sheet, User

from lti_app.models import (LMS, WIMS, WimsClass, WimsExam,
                            WimsSheet, WimsUser)


# URL to the WIMS server used for tests, the server must recognise ident 'myself' and passwd 'toto'
WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi"

# Credentials of LMS and WIMS
KEY = 'provider1'
SECRET = 'secret1'
PASSWORD = "password"
TEST_SERVER = "https://testserver"



def command(cmd):
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    out, err = p.communicate()
    if p.returncode:
        raise RuntimeError(
            "Return code : " + str(p.returncode) + " - " + err.decode() + out.decode())
    return p.returncode, out.decode().strip(), err.decode()



def untar_archive():
    """Deploy the archive 'resources/6948902.tgz' into the WIMS class (assuming its running in a
    container called 'wims') and return its qclass."""
    archive = os.path.join(os.path.dirname(__file__), "resources/6948902.tgz")
    command("docker cp %s wims:/home/wims/log/classes/" % archive)
    command('docker exec wims bash -c '
            '"tar -xzf /home/wims/log/classes/6948902.tgz -C /home/wims/log/classes/"')
    command('docker exec wims bash -c "chmod 644 /home/wims/log/classes/6948902/.def"')
    command('docker exec wims bash -c "chown wims:wims /home/wims/log/classes/6948902 -R"')
    command('docker exec wims bash -c "rm /home/wims/log/classes/6948902.tgz"')
    command("docker exec wims bash -c "
            "\"echo ':6948902,20200626,Institution,test,en,0,H4,dmi,S S,+myself/myclass+,' "
            '>> /home/wims/log/classes/.index"')
    return 6948902



urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])



class BaseLinksViewTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.lms1 = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                      name="No WIMS", key="provider1", secret="secret1")
        cls.lms2 = LMS.objects.create(guid="elearning.test.fr", url="https://elearning.test.fr/",
                                      name="One WIMS", key="provider2", secret="secret1")
        cls.lms3 = LMS.objects.create(guid="elearning.test.fr", url="https://elearning.test.fr/",
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
        cls.class1 = WimsClass.objects.create(lms=cls.lms3, wims=cls.wims2, lms_guid=1,
                                              qclass=c1.qclass, name=c1.name)
        cls.class2 = WimsClass.objects.create(lms=cls.lms3, wims=cls.wims2, lms_guid=2,
                                              qclass=c2.qclass, name=c2.name)
        
        cls.sheet1 = Sheet("Sheet1", "Desc1")
        cls.sheet2 = Sheet("Sheet2", "Desc2")
        c2.additem(cls.sheet1)
        c2.additem(cls.sheet2)
        cls.wsheet1 = WimsSheet.objects.create(wclass=cls.class1, qsheet=cls.sheet1.qsheet,
                                               lms_guid=1)
        
        cls.exam1 = Exam("Exam1", "Desc1")
        cls.exam2 = Exam("Exam2", "Desc2")
        c2.additem(cls.exam1)
        c2.additem(cls.exam2)
        cls.wexam1 = WimsExam.objects.create(wclass=cls.class1, qexam=cls.sheet1.qsheet,
                                             lms_guid=1)



class BaseGradeLinksViewTestCase(LiveServerTestCase):
    
    def setUp(self):
        self.client = Client()
        self.url_ok = self.live_server_url + reverse("lti:test_xml_ok")
        self.url_error = self.live_server_url + reverse("lti:test_xml_error")
        self.url_badly_formatted = self.live_server_url + reverse("lti:xml_badly_formatted")
        
        self.lms1 = LMS.objects.create(guid="elearning.upem.fr", url="https://elearning.u-pem.fr/",
                                       name="No WIMS", key="provider1", secret="secret1")
        self.wims2 = WIMS.objects.create(url=WIMS_URL, name="Two", ident="myself", passwd="toto",
                                         rclass="myclass")
        qclass = untar_archive()
        c1 = Class.get(WIMS_URL, "myself", "toto", qclass, "myclass")
        self.class1 = WimsClass.objects.create(lms=self.lms1, wims=self.wims2, lms_guid=1,
                                               qclass=c1.qclass, name=c1.name)
        self.user = WimsUser.objects.create(lms_guid="qcoumes", wclass=self.class1, quser="qcoumes")
        
        self.sheet1 = c1.getitem(1, Sheet)
        self.wsheet1 = WimsSheet.objects.create(wclass=self.class1, qsheet=self.sheet1.qsheet,
                                                lms_guid=1)
        
        self.exam1 = c1.getitem(1, Exam)
        self.wexam1 = WimsExam.objects.create(wclass=self.class1, qexam=self.sheet1.qsheet,
                                              lms_guid=1)
