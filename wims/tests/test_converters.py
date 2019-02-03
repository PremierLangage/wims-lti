import re

from django.test import TestCase

from wims.converters import DNSConverter



class DNSConverterTestCase(TestCase):
    
    def test_regex(self):
        r = re.compile(DNSConverter.regex)
        
        self.assertTrue(r.fullmatch("upem.fr"))
        self.assertTrue(r.fullmatch("upem"))
        self.assertTrue(r.fullmatch("upem" + ".fr" * 100))
        self.assertTrue(r.fullmatch("upem7.fr"))
        self.assertTrue(r.fullmatch("u-pem.fr"))
        self.assertTrue(r.fullmatch("u_pem.fr"))
        self.assertTrue(r.fullmatch("_upem.fr"))
        
        self.assertFalse(r.fullmatch("-upem.fr"))
        self.assertFalse(r.fullmatch("upem-.fr"))
    
    
    def test_to_python(self):
        self.assertEqual("upem.fr", DNSConverter().to_python("upem.fr"))
    
    
    def test_to_url(self):
        self.assertEqual("upem.fr", DNSConverter().to_url("upem.fr"))
