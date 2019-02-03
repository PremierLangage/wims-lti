# -*- coding: utf-8 -*-
#
#  validator.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging
import time

from django.conf import settings
from oauthlib.oauth1 import RequestValidator as BaseRequestValidator


logger = logging.getLogger(__name__)



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
