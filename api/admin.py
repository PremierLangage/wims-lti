from django.contrib import admin
from django.contrib.auth.models import Group

from api import models



@admin.register(models.LMS)
class LMSAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid')



@admin.register(models.WIMS)
class WIMSAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url')



@admin.register(models.WimsClass)
class WIMSClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'wims', 'lms', 'lms_uuid', 'qclass')



@admin.register(models.WimsUser)
class WIMSUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'lms', 'lms_uuid', 'wclass', 'quser')



admin.site.unregister(Group)
