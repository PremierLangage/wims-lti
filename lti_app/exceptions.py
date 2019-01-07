class BadRequestException(Exception):
    """Raised if the LTI request is not valid."""
    pass



class UnkownConsumerException(Exception):
    """Raised if the consumer key reiceved is not in settings.LTI_OAUTH_CREDENTIALS."""
    pass



class InvalidSecretExecption(Exception):
    """Raised when the secret received does not correspond to the consumer key in
    settings.LTI_OAUTH_CREDENTIALS."""
