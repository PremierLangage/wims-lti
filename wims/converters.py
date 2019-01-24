# -*- coding: utf-8 -*-
#
#  converters.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

class DNSConverter:
    """Implements a DNS converter to use in urls."""
    
    regex = r"\w(-?\w)*(\.\w(-?\w)*)*"
    
    
    @staticmethod
    def to_python(value):
        return value
    
    
    @staticmethod
    def to_url(value):
        return value
