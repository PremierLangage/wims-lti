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

import requests
from defusedxml import ElementTree
from django.core.validators import MinLengthValidator, URLValidator
from django.db import models
from oauthlib.oauth1.rfc5849 import Client
from wimsapi import AdmRawError, Class, Exam, Sheet

from lti_app.validator import ModelsValidator


logger = logging.getLogger(__name__)

wims_help = "See 'https://wimsapi.readthedocs.io/#configuration' for more informations"
lms_guid_help = ("Must be equal to the parameter 'tool_consumer_instance_guid' sent by the LMS in "
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
    guid = models.CharField(
        max_length=2048, help_text=lms_guid_help, verbose_name="GUID", default=None
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
        verbose_name="Default duration", help_text=expiration_help,
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



class WimsClass(models.Model):
    """Represents a class on a WIMS server."""
    lms = models.ForeignKey(LMS, models.CASCADE)
    lms_guid = models.CharField(max_length=256, default=None)
    wims = models.ForeignKey(WIMS, models.CASCADE)
    qclass = models.CharField(max_length=256, default=None)
    name = models.CharField(max_length=2048, default=None)
    
    class Meta:
        verbose_name_plural = "WimsClasses"
        unique_together = (("lms", "lms_guid", "wims"), ("wims", "qclass"),)
    
    def __str__(self):
        return "%s (%s)" % (self.name, self.qclass)



class WimsUser(models.Model):
    """Represent an user on a WIMS server."""
    lms_guid = models.CharField(max_length=256, null=True)
    wclass = models.ForeignKey(WimsClass, models.CASCADE)
    quser = models.CharField(max_length=256, default=None)
    
    class Meta:
        verbose_name_plural = "WimsUsers"
        unique_together = (("quser", "wclass"),)
    
    def __str__(self):
        return "%s" % self.quser



class WimsSheet(models.Model):
    """Represents a Sheet on the WIMS server."""
    wclass = models.ForeignKey(WimsClass, models.CASCADE)
    lms_guid = models.CharField(max_length=256, default=None)
    qsheet = models.CharField(max_length=256, null=True, default=None)
    
    class Meta:
        unique_together = (("qsheet", "wclass"),)



class WimsExam(models.Model):
    """Represents an Exam on the WIMS server."""
    wclass = models.ForeignKey(WimsClass, models.CASCADE)
    lms_guid = models.CharField(max_length=256, default=None)
    qexam = models.CharField(max_length=256, null=True, default=None)
    
    class Meta:
        unique_together = (("qexam", "wclass"),)



class GradeLinkBase(models.Model):
    """Store links to send grade back to the LMS."""
    user = models.ForeignKey(WimsUser, models.CASCADE)
    sourcedid = models.CharField(max_length=256)
    url = models.URLField(max_length=1023)
    lms = models.ForeignKey(LMS, models.CASCADE)
    
    class Meta:
        abstract = True
    
    def send_back(self, grade, activity):
        """Send the given grade back to the lms."""
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, "../lti_app/ressources/replace.xml")
        with open(path) as f:
            content = (f.read() % (self.sourcedid, str(grade))).encode()
        
        headers = {
            "Content-Type":   "application/xml",
            "Content-Length": str(len(content)),
        }
        c = Client(client_key=self.lms.key, client_secret=self.lms.secret)
        uri, headers, body = c.sign(self.url, "POST", body=content, headers=headers)
        response = requests.post(uri, data=body, headers=headers)

        ident = activity.qsheet if isinstance(activity, WimsSheet) else activity.qexam
        try:
            root = ElementTree.fromstring(response.text)
            test = 200 <= response.status_code < 300 and root[0][0][2][0].text == "success"
            if not test:  # pragma: no cover
                logger.warning(
                    ("Consumer sent an error response after sending grade for user '%s' and "
                     "sheet '%s' in class '%s': %s")
                    % (self.user.quser, ident, activity.wclass.qclass, root[0][0][2][2].text)
                )
        except Exception:
            logger.exception(
                ("Consumer sent a badly formatted response after sending grade for user '%s' and "
                 "sheet '%s' in class '%s': ")
                % (self.user.quser, ident, activity.wclass.qclass)
            )



class GradeLinkSheet(GradeLinkBase):
    """Store link of a Sheet."""
    
    sheet = models.ForeignKey(WimsSheet, models.CASCADE)
    
    class Meta:
        unique_together = (("user", "sheet"),)
    
    @classmethod
    def send_back_all(cls, wclass, sheet):
        """Send the score of the sheet of every user back to the LMS. The score used
        it the the one set by the teacher at the sheet creation for WIMS > 4.18, else
        the cumul score."""
        try:
            wims = wclass.wims
            grades = Class.get(
                wims.url, wclass.wims.ident, wims.passwd, wclass.qclass, wims.rclass
            ).getitem(sheet.qsheet, Sheet).scores()
        except AdmRawError as e:
            if "There is no user in this class" in str(e):
                return
            raise  # pragma: no cover
        
        for grade in grades:
            user = WimsUser.objects.get(wclass=wclass, quser=grade.user.quser)
            try:
                gl = GradeLinkSheet.objects.get(user=user, sheet=sheet)
            except GradeLinkSheet.DoesNotExist:
                continue
            score = grade.score if grade.score != -1 else grade.best // 10
            gl.send_back(score, gl.sheet)



class GradeLinkExam(GradeLinkBase):
    """Store link of a Sheet."""
    
    exam = models.ForeignKey(WimsExam, models.CASCADE)
    
    class Meta:
        unique_together = (("user", "exam"),)
    
    @classmethod
    def send_back_all(cls, wclass, exam):
        """Send the score of the exam of every user back to the LMS."""
        try:
            wims = wclass.wims
            grades = Class.get(
                wims.url, wclass.wims.ident, wims.passwd, wclass.qclass, wims.rclass
            ).getitem(exam.qexam, Exam).scores()
        except AdmRawError as e:
            if "There is no user in this class" in str(e):
                return
            raise
        
        for grade in grades:
            user = WimsUser.objects.get(wclass=wclass, quser=grade.user.quser)
            try:
                gl = GradeLinkExam.objects.get(user=user, exam=exam)
            except GradeLinkExam.DoesNotExist:
                continue
            score = grade.score
            gl.send_back(score, gl.exam)
