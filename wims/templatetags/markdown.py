# -*- coding: utf-8 -*-
#
#  markdown.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#


import markdown as md
from django import template


register = template.Library()



@register.filter(is_safe=True)
def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])
