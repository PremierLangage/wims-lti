# -*- coding: utf-8 -*-
#
#  models.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

from django.core.validators import RegexValidator, URLValidator
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
    ident = models.CharField(max_length=2048)
    passwd = models.CharField(max_length=2048)
    rclass = models.CharField(max_length=2048)
    url = models.CharField(
            max_length=2048, unique=True, db_index=True,
            validators=[URLValidator(['http', 'https'], message="Enter a valid URL")]
    )
    dns = models.CharField(
            max_length=253, unique=True, db_index=True,
            validators=[RegexValidator(DNSConverter.regex, "Enter a valid DNS")]
    )
    
    
    class Meta:
        verbose_name_plural = "WIMS"



class LMS(models.Model):
    """Represents a LMS."""
    uuid = models.CharField(max_length=2048, primary_key=True)
    
    
    class Meta:
        verbose_name_plural = "LMS"



class WimsClass(models.Model):
    """Represents a class on a WIMS server."""
    wims = models.ForeignKey(WIMS, models.CASCADE)
    lms = models.ForeignKey(LMS, models.CASCADE)
    wims_uuid = models.CharField(max_length=256)
    lms_uuid = models.CharField(max_length=256)
    
    
    class Meta:
        verbose_name_plural = "WimsClasses"
        unique_together = (("lms", "lms_uuid"), ("wims", "wims_uuid"),)
        indexes = [models.Index(fields=['lms', 'lms_uuid', 'wims'])]



class WimsUser(models.Model):
    """Represent an user on a WIMS server."""
    lms = models.ForeignKey(LMS, models.CASCADE)
    lms_uuid = models.CharField(max_length=256)
    quser = models.CharField(max_length=256)
    wclass = models.ForeignKey(WimsClass, models.CASCADE)
    
    
    class Meta:
        verbose_name_plural = "WimsUsers"
        unique_together = (("lms", "lms_uuid"), ("quser", "wclass"),)
        indexes = [models.Index(fields=['lms', 'lms_uuid', 'wclass'])]
