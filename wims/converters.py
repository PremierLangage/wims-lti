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
    
    
    def to_python(self, value):
        return value
    
    
    def to_url(self, value):
        return value
