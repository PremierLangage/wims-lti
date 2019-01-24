# -*- coding: utf-8 -*-
#
#  exceptions.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

class BadRequestException(Exception):
    """Raised if the LTI request is not valid."""
    pass