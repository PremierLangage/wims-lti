# -*- coding: utf-8 -*-
#
#  models.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#
import logging
from datetime import timedelta

import wimsapi
from django.core.validators import URLValidator
from django.db import models
from django.urls import reverse

from lti_app.validator import ModelsValidator


logger = logging.getLogger(__name__)

wims_help = "See 'https://wimsapi.readthedocs.io/#configuration' for more informations"
lms_uuid_help = ("Must be equal to the parameter 'tool_consumer_instance_guid' sent by the LMS in "
                 "the LTI request. It is commonly the DNS of the LMS.")
class_limit_help = ("This is the classes default maximum student (between [5, 500]. This parameter "
                    "is used at class creation and can be later changed individually for each class"
                    " on the WIMS server by the supervisor.")
expiration_help = ("This is the classes default duration (format is 'day hours:minutes:seconds', "
                   "default is 365 days) before expiration. This parameter is used at class "
                   "creation and can be later changed individually for each class on the ""WIMS "
                   "server by the supervisor.")



class LMS(models.Model):
    """Represents a LMS."""
    uuid = models.CharField(
        max_length=2048, help_text=lms_uuid_help, verbose_name="UUID"
    )
    name = models.CharField(max_length=2048, null=False)
    url = models.CharField(
        max_length=2048, verbose_name="URL",
        validators=[URLValidator(['http', 'https'], message="Please enter a valid URL")]
    )
    
    
    class Meta:
        verbose_name_plural = "LMS"



class WIMS(models.Model):
    """Represents a WIMS server.
    
    For more information about <ident>, <passwd> et <rclass>, see:
    https://wimsapi.readthedocs.io/en/latest/#configuration
    
    Parameters:
        * url - URL to the api server's CGI, including scheme,
                e.g.: 'http://wims.unice.fr/~wims/wims.cgi'
        * dns - DNS of the api server, e.g.: 'api.unice.fr'
        * ident - Identifier of the api server.
        * passwd - Password of the api server.
        * rclass - Identifier used for each class of this WIMS server."""
    name = models.CharField(max_length=2048)
    url = models.CharField(
        max_length=2048, unique=True, db_index=True, verbose_name="URL",
        validators=[URLValidator(['http', 'https'], message="Please enter a valid URL")],
        help_text="URL must point to the WIMS' server cgi.",
    )
    class_limit = models.PositiveSmallIntegerField(
        verbose_name="Default student limit", help_text=class_limit_help, default=150,
        validators=[ModelsValidator.limit_validator],
    )
    expiration = models.DurationField(
        verbose_name="Default expiration date", help_text=expiration_help,
        default=timedelta(days=365), validators=[ModelsValidator.expiration_validator],
    )
    ident = models.CharField(max_length=2048, help_text=wims_help)
    passwd = models.CharField(max_length=2048, help_text=wims_help)
    rclass = models.CharField(max_length=2048, help_text=wims_help)
    allowed_lms = models.ManyToManyField(LMS)
    
    
    class Meta:
        verbose_name_plural = "WIMS"
    
    
    def __str__(self):
        return "%s (%s)" % (self.name, self.url)
    
    
    def serialize(self, request):
        return {
            "pk":      self.pk,
            "name":    self.name,
            "url":     self.url,
            "lti_url": request.build_absolute_uri(reverse("lti:wims_class", args=[self.pk]))
        }



class WimsClass(models.Model):
    """Represents a class on a WIMS server."""
    lms = models.ForeignKey(LMS, models.CASCADE)
    lms_uuid = models.CharField(max_length=256)
    wims = models.ForeignKey(WIMS, models.CASCADE)
    qclass = models.CharField(max_length=256)
    name = models.CharField(max_length=2048)
    
    
    class Meta:
        verbose_name_plural = "WimsClasses"
        unique_together = (("lms", "lms_uuid"), ("wims", "qclass"),)
    
    
    def __str__(self):
        return "%s (%s)" % (self.name, self.qclass)
    
    
    def serialize(self):
        return {
            "pk":     self.pk,
            "name":   self.name,
            "qclass": self.qclass,
        }



class WimsUser(models.Model):
    """Represent an user on a WIMS server."""
    lms_uuid = models.CharField(max_length=256, null=True, unique=True)
    wclass = models.ForeignKey(WimsClass, models.CASCADE)
    quser = models.CharField(max_length=256)
    
    
    class Meta:
        verbose_name_plural = "WimsUsers"
        unique_together = (("quser", "wclass"),)
    
    
    def __str__(self):
        return "%s" % self.quser



class Activity(models.Model):
    """Represents a Sheet on the WIMS server."""
    wclass = models.ForeignKey(WimsClass, models.CASCADE)
    lms_uuid = models.CharField(max_length=256)
    qsheet = models.CharField(max_length=256)
    
    
    class Meta:
        verbose_name_plural = "Activities"
        unique_together = (("qsheet", "wclass"),)



class GradeLink(models.Model):
    """Store link to send grade back to the LMS."""
    user = models.ForeignKey(WimsUser, models.CASCADE)
    activity = models.ForeignKey(Activity, models.CASCADE)
    sourcedid = models.CharField(max_length=256)
    url = models.URLField(max_length=1023)
    
    
    class Meta:
        unique_together = (("user", "activity"),)
    
    
    @classmethod
    def send_back(cls, wclass, qsheet):
        wapi = wimsapi.WimsAPI(wclass.wims.url, wclass.wims.ident, wclass.wims.passwd)
        bol, response = wapi.getsheetscores(wclass.qclass, wclass.wims.rclass, qsheet)
        if not bol:
            raise wimsapi.AdmRawError(response['message'])
        
        for infos in response['data_scores']:
            user = WimsUser.objects.get(quser=infos['id'], wclass=wclass)
            grade = sum(infos['sheet_got_details']) / len(infos['sheet_got_details'])
