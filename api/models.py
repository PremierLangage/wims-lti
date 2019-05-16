# -*- coding: utf-8 -*-
#
#  models.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging
import os
from datetime import timedelta
from defusedxml import ElementTree

import requests
import wimsapi
from django.core.validators import MinLengthValidator, URLValidator
from django.db import models
from django.urls import reverse
from oauthlib.oauth1.rfc5849 import Client

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
        max_length=2048, help_text=lms_uuid_help, verbose_name="UUID", default=None
    )
    name = models.CharField(max_length=2048, default=None)
    url = models.CharField(
        max_length=2048, verbose_name="URL", default=None,
        validators=[URLValidator(['http', 'https'], message="Please enter a valid URL")]
    )
    key = models.CharField(
        max_length=128, unique=True, validators=[MinLengthValidator(3)], default=None
    )
    secret = models.CharField(max_length=128, validators=[MinLengthValidator(3)], default=None)
    
    
    class Meta:
        verbose_name_plural = "LMS"
        indexes = [
            models.Index(fields=['key']),
        ]
    
    
    def __str__(self):
        return "%s (%s)" % (self.name, self.url)



class WIMS(models.Model):
    """Represents a WIMS server.
    
    For more information about <ident>, <passwd> et <rclass>, see:
    https://wimsapi.readthedocs.io/en/latest/#configuration"""
    name = models.CharField(max_length=2048, default=None)
    url = models.CharField(
        max_length=2048, unique=True, db_index=True, verbose_name="URL", default=None,
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
    ident = models.CharField(max_length=2048, help_text=wims_help, default=None)
    passwd = models.CharField(max_length=2048, help_text=wims_help, default=None)
    rclass = models.CharField(max_length=2048, help_text=wims_help, default=None)
    allowed_lms = models.ManyToManyField(LMS, blank=True)
    
    
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
    lms_uuid = models.CharField(max_length=256, default=None)
    wims = models.ForeignKey(WIMS, models.CASCADE)
    qclass = models.CharField(max_length=256, default=None)
    name = models.CharField(max_length=2048, default=None)
    
    
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
    lms_uuid = models.CharField(max_length=256, null=True)
    wclass = models.ForeignKey(WimsClass, models.CASCADE)
    quser = models.CharField(max_length=256, default=None)
    
    
    class Meta:
        verbose_name_plural = "WimsUsers"
        unique_together = (("quser", "wclass"),)
    
    
    def __str__(self):
        return "%s" % self.quser



class Activity(models.Model):
    """Represents a Sheet on the WIMS server."""
    wclass = models.ForeignKey(WimsClass, models.CASCADE)
    lms_uuid = models.CharField(max_length=256, default=None)
    qsheet = models.CharField(max_length=256, default=None)
    
    
    class Meta:
        verbose_name_plural = "Activities"
        unique_together = (("qsheet", "wclass"),)



class GradeLink(models.Model):
    """Store link to send grade back to the LMS."""
    user = models.ForeignKey(WimsUser, models.CASCADE)
    activity = models.ForeignKey(Activity, models.CASCADE)
    sourcedid = models.CharField(max_length=256, default=None)
    url = models.URLField(max_length=1023, default=None)
    
    
    class Meta:
        unique_together = (("user", "activity"),)
    
    
    def send_back(self, grade):
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, "ressources/replace.xml")
        with open(path) as f:
            content = (f.read() % (self.sourcedid, str(grade))).encode()
        
        headers = {
            "Content-Type":   "application/xml",
            "Content-Length": str(len(content)),
        }
        c = Client(client_key=self.activity.wclass.lms.key,
                   client_secret=self.activity.wclass.lms.secret)
        uri, headers, body = c.sign(self.url, "POST", body=content,
                                    headers=headers)
        response = requests.post(uri, data=body, headers=headers)
        
        root = ElementTree.fromstring(response.text)
        if not (200 <= response.status_code < 300 and root[0][0][2][0].text == "success"):
            logger.warning(("Consumer sent an error response after sending grade for user '%s' and "
                            "activity '%s' in class '%s': %s")
                           % (self.user.quser, self.activity.qsheet, self.activity.wclass.qclass,
                              root[0][0][2][2].text))
    
    
    @classmethod
    def send_back_all(cls, wclass, activity):
        wapi = wimsapi.WimsAPI(wclass.wims.url, wclass.wims.ident, wclass.wims.passwd)
        bol, response = wapi.getsheetscores(wclass.qclass, wclass.wims.rclass, activity.qsheet)
        if not bol:
            raise wimsapi.AdmRawError(response['message'])
        
        for infos in response['data_scores']:
            if not infos['got_detail']:
                continue
            user = WimsUser.objects.get(wclass=wclass, quser=infos['id'])
            gl = cls.objects.get(user=user, activity=activity)
            grade = sum(infos['got_detail']) / len(infos['got_detail']) / 10
            gl.send_back(grade)
