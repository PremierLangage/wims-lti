# -*- coding: utf-8 -*-
#
#  models.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

from django.core.validators import RegexValidator
from django.db import models

from wims.converters import DNSConverter



class WIMS(models.Model):
    """Represents a WIMS server.
    
    For more information about <ident>, <passwd> et <rclass>, see:
    https://wimsapi.readthedocs.io/en/latest/#configuration
    
    Parameters:
        * url - URL to the wims server's CGI, including scheme,
                e.g.: 'http://wims.unice.fr/~wims/wims.cgi'
        * dns - DNS of the wims server, e.g.: 'wims.unice.fr'
        * ident - Identifier of the wims server.
        * passwd - Password of the wims server.
        * rclass - Identifier used for each class of this WIMS server."""
    url = models.CharField(max_length=2048, unique=True)
    dns = models.CharField(max_length=2048, unique=True,
                           validators=[RegexValidator(DNSConverter.regex, "Not a valid DNS")])
    ident = models.CharField(max_length=2048)
    passwd = models.CharField(max_length=2048)
    rclass = models.CharField(max_length=2048)
    
    
    class Meta:
        verbose_name_plural = "wims"



class LMS(models.Model):
    """Represents a WIMS server.

       For more information about <ident>, <passwd> et <rclass>, see:
       https://wimsapi.readthedocs.io/en/latest/#configuration

       Parameters:
           * uuid - UUID of the LMS as sent by the LTI request."""
    uuid = models.CharField(max_length=2048, primary_key=True)
    
    
    class Meta:
        verbose_name_plural = "lms"



class WimsClass(models.Model):
    wims = models.ForeignKey(WIMS, models.CASCADE)
    lms = models.ForeignKey(LMS, models.CASCADE)
    wims_uuid = models.CharField(max_length=16)
    lms_uuid = models.CharField(max_length=16)
    
    
    class Meta:
        unique_together = (("lms", "lms_uuid"), ("wims", "wims_uuid"),)
        verbose_name_plural = "wimsclasses"
        indexes = [models.Index(fields=['lms', 'lms_uuid', 'wims'])]



class WimsUser(models.Model):
    lms = models.ForeignKey(LMS, models.CASCADE)
    lms_uuid = models.CharField(max_length=16)
    quser = models.CharField(max_length=256)
    wclass = models.ForeignKey(WimsClass, models.CASCADE)
    
    
    class Meta:
        unique_together = (("lms", "lms_uuid"), ("quser", "wclass"),)
        indexes = [models.Index(fields=['lms', 'lms_uuid', 'wclass'])]
