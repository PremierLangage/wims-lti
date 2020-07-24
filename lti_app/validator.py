# -*- coding: utf-8 -*-
#
#  validators.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import datetime
import logging
import time
from typing import Callable, Optional, Union

import wimsapi
from django.apps import apps
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import EmailValidator
from django.http import HttpRequest
from oauthlib.oauth1 import RequestValidator as BaseRequestValidator

from lti_app.exceptions import BadRequestException


logger = logging.getLogger(__name__)



def validate(validator: Callable[[any], bool], value: any, message: str):
    """Check <value> against the function <validator>.
    Raising BadRequestException(message) if check failed."""
    if not validator(value):
        raise BadRequestException(message)



class CustomParameterValidator:
    """Allow to validate known custom parameters"""
    
    
    @staticmethod
    def email_validator(email: Optional[str]) -> bool:
        if email is not None:
            try:
                EmailValidator()(email)
            except ValidationError:
                return False
        return True
    
    
    @staticmethod
    def lang_validator(lang: Optional[str]) -> bool:
        return lang is None or lang in wimsapi.wclass.LANG
    
    
    @staticmethod
    def level_validator(level: Optional[str]) -> bool:
        return level is None or level in wimsapi.wclass.LEVEL
    
    
    @staticmethod
    def expiration_syntax_validator(expiration: Optional[str]) -> bool:
        if expiration is not None:
            try:
                datetime.datetime.strptime(expiration, "%Y%m%d").date()
            except ValueError:
                return False
        return True
    
    @staticmethod
    def expiration_date_validator(expiration: Optional[str]) -> bool:
        if expiration is not None:
            date = datetime.datetime.strptime(expiration, "%Y%m%d").date()
            now = datetime.date.today()
            start = now + datetime.timedelta(days=31)
            end = now + datetime.timedelta(days=365)
            return start <= date <= end
        return True
    
    
    @staticmethod
    def limit_validator(limit: Optional[Union[str, int]]) -> bool:
        return limit is None or (limit.isdigit() and 5 <= int(limit) <= 500)



class ModelsValidator:
    """Provide validator for models' fields."""
    
    
    @staticmethod
    def limit_validator(limit: int):
        if not (5 <= int(limit) <= 500):
            raise ValidationError("Default student limit must be in [5, 500].")
    
    
    @staticmethod
    def expiration_validator(expiration: datetime.timedelta):
        now = datetime.date.today()
        start = now + datetime.timedelta(days=31)
        test = now + expiration
        end = now + datetime.timedelta(days=365)
        if not (start <= test <= end):
            raise ValidationError(
                "Expiration date must be between '31 00:00:00' and '365 00:00:00'"
            )



class RequestValidator(BaseRequestValidator):
    """Implements a RequestValidator according to
    https://oauthlib.readthedocs.io/en/latest/oauth1/validator.html"""
    
    client_key_length = (3, 100)
    nonce_length = (3, 100)
    
    
    def validate_client_key(self, client_key: str, request: HttpRequest) -> bool:
        """Check that a LMS with this client_key exists."""
        LMS = apps.get_model('lti_app.LMS')
        try:
            return bool(LMS.objects.get(key=client_key))
        except LMS.DoesNotExist:
            logger.debug("LTI Authentification aborted: Unknown consumer key: '%s'" % client_key)
            raise PermissionDenied("Unknown consumer key: '%s'" % client_key)
    
    
    def validate_timestamp_and_nonce(self, client_key: str, timestamp: str, nonce: str,
                                     request: HttpRequest, request_token: str = None,
                                     access_token: str = None) -> bool:
        """Check that timestamp is not older than 30 minutes."""
        return int(time.time()) - int(timestamp) < 1800
    
    
    def get_client_secret(self, client_key: str, request: HttpRequest) -> str:
        """Retrieve the secret corresponding to the LMS using client_key."""
        LMS = apps.get_model('lti_app.LMS')
        return LMS.objects.get(key=client_key).secret
