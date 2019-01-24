# -*- coding: utf-8 -*-
#
#  validator.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import time

from django.conf import settings
from oauthlib.oauth1 import RequestValidator as BaseRequestValidator



class RequestValidator(BaseRequestValidator):
    """Implements a RequestValidator according to
    https://oauthlib.readthedocs.io/en/latest/oauth1/validator.html"""
    
    
    def validate_client_key(self, client_key, request):
        return client_key in settings.LTI_OAUTH_CREDENTIALS
    
    
    def validate_request_token(self, client_key, token, reques):
        return True
    
    
    def validate_access_token(self, client_key, token, reques):
        return True
    
    
    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request,
                                     request_token=None, access_token=None):
        return int(time.time()) - int(timestamp) < 1800
    
    
    def validate_redirect_uri(self, client_key, redirect_uri, request):
        return True
    
    
    def validate_requested_realms(self, client_key, realms, request):
        return True
    
    
    def validate_realms(self, client_key, token, request, uri=None, realms=None):
        return True
    
    
    def validate_verifier(self, client_key, token, verifier, request):
        return True
    
    
    def invalidate_request_token(self, client_key, request_token, request):
        pass
    
    
    def get_client_secret(self, client_key, request):
        return settings.LTI_OAUTH_CREDENTIALS.get("client_key", "dummy")
    
    
    def get_request_token_secret(self, client_key, token, reques):
        return "dummy"
    
    
    def get_access_token_secret(self, client_key, token, request):
        return "dummy"
    
    
    def get_rsa_key(self, client_key, request):
        return "dummy"
    
    
    def get_realms(self, token, request):
        return []
    
    
    def get_default_realms(self, client_key, request):
        return []
    
    
    def get_redirect_uri(self, token, request):
        return "dummy"
    
    
    def save_request_token(self, token, request):
        pass
    
    
    def save_verifier(self, token, verifier, request):
        pass
    
    
    def save_access_token(self, token, request):
        pass
    
    
    def verify_realms(self, token, realms, request):
        return True
    
    
    def verify_request_token(self, token, request):
        return True
    
    
    @property
    def dummy_client(self):
        return "dummy"
    
    
    @property
    def dummy_request_token(self):
        return "dummy"
    
    
    @property
    def dummy_access_token(self):
        return "dummy"
