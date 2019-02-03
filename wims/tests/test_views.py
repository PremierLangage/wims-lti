import os

from django.shortcuts import reverse
from django.test import Client, TestCase

from wims.models import LMS, WIMS
from wims.templatetags.markdown import markdown


# URL to the WIMS server used for tests, the server must recogned ident 'myself' and passwd 'toto'
WIMS_URL = os.getenv("WIMS_URL") or "http://localhost:7777/wims/wims.cgi"



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
