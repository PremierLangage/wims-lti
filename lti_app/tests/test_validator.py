# -*- coding: utf-8 -*-
#
#  test_validators.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from lti_app.exceptions import BadRequestException
from lti_app.validator import CustomParameterValidator, ModelsValidator, validate



class CustomParameterValidatorTestCase(TestCase):
    
    def test_email_validator(self):
        self.assertTrue(CustomParameterValidator.email_validator("name@host.com"))
        self.assertTrue(CustomParameterValidator.email_validator(None))
        self.assertFalse(CustomParameterValidator.email_validator("#wrong@h@st.com"))
    
    
    def test_lang_validator(self):
        self.assertTrue(CustomParameterValidator.lang_validator("en"))
        self.assertTrue(CustomParameterValidator.lang_validator(None))
        self.assertFalse(CustomParameterValidator.lang_validator("unknown"))
    
    
    def test_level_validator(self):
        self.assertTrue(CustomParameterValidator.level_validator("H4"))
        self.assertTrue(CustomParameterValidator.level_validator(None))
        self.assertFalse(CustomParameterValidator.level_validator("unknown"))
    
    
    def test_limit_validator(self):
        self.assertTrue(CustomParameterValidator.limit_validator("120"))
        self.assertTrue(CustomParameterValidator.limit_validator(None))
        self.assertFalse(CustomParameterValidator.limit_validator("0"))
        self.assertFalse(CustomParameterValidator.limit_validator("999999999"))
    
    def test_expiration_syntax_validator(self):
        self.assertTrue(CustomParameterValidator.expiration_syntax_validator("20200101"))
        # DDMMYY
        self.assertFalse(CustomParameterValidator.expiration_syntax_validator("01012020"))
        self.assertFalse(CustomParameterValidator.expiration_syntax_validator("Wrong format"))
    
    def test_expiration_date_validator(self):
        now = datetime.date.today()
        less_than_a_month = (now + datetime.timedelta(days=30)).strftime("%Y%m%d")
        month = (now + datetime.timedelta(days=31)).strftime("%Y%m%d")
        months = (now + datetime.timedelta(days=150)).strftime("%Y%m%d")
        year = (now + datetime.timedelta(days=365)).strftime("%Y%m%d")
        more_than_a_year = (now + datetime.timedelta(days=366)).strftime("%Y%m%d")
        
        self.assertTrue(CustomParameterValidator.expiration_date_validator(month))
        self.assertTrue(CustomParameterValidator.expiration_date_validator(months))
        self.assertTrue(CustomParameterValidator.expiration_date_validator(year))
        self.assertFalse(CustomParameterValidator.expiration_date_validator(less_than_a_month))
        self.assertFalse(CustomParameterValidator.expiration_date_validator(more_than_a_year))
        
    
    
    def test_validate(self):
        validate(CustomParameterValidator.lang_validator, "en", "Unknown language")  # Ok
        
        with self.assertRaisesMessage(BadRequestException, "Unknown language"):
            validate(CustomParameterValidator.lang_validator, "abc", "Unknown language")



class ModelsValidatorTestCase(TestCase):
    
    def test_expiration_validator(self):
        less_than_a_month = datetime.timedelta(days=30)
        month = datetime.timedelta(days=31)
        months = datetime.timedelta(days=150)
        year = datetime.timedelta(days=365)
        more_than_a_year = datetime.timedelta(days=366)
        
        ModelsValidator.expiration_validator(month)
        ModelsValidator.expiration_validator(months)
        ModelsValidator.expiration_validator(year)
        with self.assertRaises(ValidationError):
            ModelsValidator.expiration_validator(less_than_a_month)
        with self.assertRaises(ValidationError):
            ModelsValidator.expiration_validator(more_than_a_year)
    
    
    def test_limit_validator(self):
        ModelsValidator.limit_validator(5)
        ModelsValidator.limit_validator(120)
        ModelsValidator.limit_validator(500)
        
        with self.assertRaises(ValidationError):
            ModelsValidator.limit_validator(0)
        with self.assertRaises(ValidationError):
            ModelsValidator.limit_validator(501)
