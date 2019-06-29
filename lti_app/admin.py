# -*- coding: utf-8 -*-
#
#  admin.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

from django.contrib import admin
from django.contrib.auth.models import Group

from lti_app import models



@admin.register(models.LMS)
class LMSAdmin(admin.ModelAdmin):
    list_display = ('name', 'guid')



@admin.register(models.WIMS)
class WIMSAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url')



@admin.register(models.WimsClass)
class WIMSClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'wims', 'lms_guid', 'qclass')



@admin.register(models.WimsUser)
class WIMSUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'lms_guid', 'wclass', 'quser')



@admin.register(models.Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'lms_guid', 'wclass', 'qsheet')



@admin.register(models.GradeLink)
class GradeLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'activity', 'sourcedid', 'url')



admin.site.unregister(Group)
