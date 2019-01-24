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


wims_help = "See 'https://wimsapi.readthedocs.io/#configuration' for more informations"



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
    dns = models.CharField(
        max_length=253, unique=True, db_index=True,
        validators=[RegexValidator("^" + DNSConverter.regex + "$", "Please enter a valid DNS")]
    )
    url = models.CharField(
        max_length=2048, unique=True, db_index=True,
        validators=[URLValidator(['http', 'https'], message="Please enter a valid URL")]
    )
    ident = models.CharField(max_length=2048, help_text=wims_help)
    passwd = models.CharField(max_length=2048, help_text=wims_help)
    rclass = models.CharField(max_length=2048, help_text=wims_help)
    
    class Meta:
        verbose_name_plural = "WIMS"



class LMS(models.Model):
    """Represents a LMS."""
    uuid = models.CharField(max_length=2048, primary_key=True)
    name = models.CharField(max_length=2048, null=False)
    
    class Meta:
        verbose_name_plural = "LMS"



class WimsClass(models.Model):
    """Represents a class on a WIMS server."""
    lms = models.ForeignKey(LMS, models.CASCADE)
    lms_uuid = models.CharField(max_length=256)
    wims = models.ForeignKey(WIMS, models.CASCADE)
    wims_uuid = models.CharField(max_length=256)
    
    class Meta:
        verbose_name_plural = "WimsClasses"
        unique_together = (("lms", "lms_uuid"), ("wims", "wims_uuid"),)
        indexes = [models.Index(fields=['lms', 'lms_uuid', 'wims'])]



class WimsUser(models.Model):
    """Represent an user on a WIMS server."""
    lms = models.ForeignKey(LMS, models.CASCADE)
    lms_uuid = models.CharField(max_length=256)
    wclass = models.ForeignKey(WimsClass, models.CASCADE)
    quser = models.CharField(max_length=256)
    
    class Meta:
        verbose_name_plural = "WimsUsers"
        unique_together = (("lms", "lms_uuid"), ("quser", "wclass"),)
        indexes = [models.Index(fields=['lms', 'lms_uuid', 'wclass'])]
