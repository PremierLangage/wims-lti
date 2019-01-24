from django.contrib import admin
from wims import models

admin.site.register(models.LMS)
admin.site.register(models.WIMS)
admin.site.register(models.WimsClass)
admin.site.register(models.WimsUser)
