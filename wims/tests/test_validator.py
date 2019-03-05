import datetime

from django.test import TestCase

from wims.exceptions import BadRequestException
from wims.validator import CustomParameterValidator, validate



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
    
    
    def test_expiration_validator(self):
        now = datetime.date.today()
        months = now.replace(month=now.month + 7).strftime("%Y%m%d")
        millenia = now.replace(year=now.year + 1000).strftime("%Y%m%d")
        year_ago = now.replace(year=now.year - 1).strftime("%Y%m%d")
        self.assertTrue(CustomParameterValidator.expiration_validator(months))
        self.assertTrue(CustomParameterValidator.expiration_validator(None))
        self.assertFalse(CustomParameterValidator.expiration_validator(millenia))
        self.assertFalse(CustomParameterValidator.expiration_validator(year_ago))
        self.assertFalse(CustomParameterValidator.expiration_validator("Wrong format"))
    
    
    def test_validate(self):
        validate(CustomParameterValidator.lang_validator, "en", "Unknown language")  # Ok
        
        with self.assertRaisesMessage(BadRequestException, "Unknown language"):
            validate(CustomParameterValidator.lang_validator, "abc", "Unknown language")
