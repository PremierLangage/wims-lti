# -*- coding: utf-8 -*-
#
#  markdown.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#


from django import template
from django.template.defaultfilters import stringfilter

import markdown as md


register = template.Library()



@register.filter(is_safe=True)
def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])
