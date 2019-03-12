# -*- coding: utf-8 -*-
#
#  validator.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import datetime
import logging
import re
import time

import wimsapi
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from oauthlib.oauth1 import RequestValidator as BaseRequestValidator

from wims.exceptions import BadRequestException


logger = logging.getLogger(__name__)



def validate(validator, value, message):
    """Check <value> against the function <validator>.
    Raising BadRequestException(message) if check failed."""
    if not validator(value):
        raise BadRequestException(message)



class CustomParameterValidator:
    
    @staticmethod
    def email_validator(email):
        if email is not None:
            try:
                EmailValidator()(email)
            except ValidationError:
                return False
        return True
    
    
    @staticmethod
    def username_validator(username):
        if username is not None:
            return bool(re.compile(r'^[a-zA-Z_]\w*$').match(username))
        return True
    
    
    @staticmethod
    def lang_validator(lang):
        return lang is None or lang in wimsapi.wclass.LANG
    
    
    @staticmethod
    def level_validator(level):
        return level is None or level in wimsapi.wclass.LEVEL
    
    
    @staticmethod
    def expiration_validator(expiration):
        if expiration is not None:
            try:
                date = datetime.datetime.strptime(expiration, "%Y%m%d").date()
                now = datetime.date.today()
                start = now + datetime.timedelta(days=31)
                end = now + datetime.timedelta(days=365)
                return start <= date <= end
            except ValueError:
                return False
        return True
    
    
    @staticmethod
    def limit_validator(limit):
        return limit is None or (limit.isdigit() and 5 <= int(limit) <= 500)



class ModelsValidator:
    
    @staticmethod
    def limit_validator(limit):
        if not (5 <= int(limit) <= 500):
            raise ValidationError("Default student limit must be in [5, 500].")
    
    
    @staticmethod
    def expiration_validator(expiration):
        now = datetime.date.today()
        start = now + datetime.timedelta(days=31)
        test = now + expiration
        end = now + datetime.timedelta(days=365)
        if not (start <= test <= end):
            raise ValidationError("Expiration date must be between '31 00:00:00' and"
                                  "'365 00:00:00'")



class RequestValidator(BaseRequestValidator):
    """Implements a RequestValidator according to
    https://oauthlib.readthedocs.io/en/latest/oauth1/validator.html"""
    
    client_key_length = (3, 100)
    nonce_length = (3, 100)
    
    
    def validate_client_key(self, client_key, request):
        """Check that client_key is declared in LTI_OAUTH_CREDENTIALS."""
        return client_key in settings.LTI_OAUTH_CREDENTIALS
    
    
    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request,
                                     request_token=None, access_token=None):
        """Check that timestamp is not older than 30 minutes."""
        return int(time.time()) - int(timestamp) < 1800
    
    
    def get_client_secret(self, client_key, request):
        """Retrieve the secret from  LTI_OAUTH_CREDENTIALS with the given client_key, 'dummy'
        if not found."""
        return settings.LTI_OAUTH_CREDENTIALS.get(client_key, "dummy")
