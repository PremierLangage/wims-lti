from django.db import models



class WIMS(models.Model):
    url = models.CharField(max_length=2048, primary_key=True)
    ident = models.CharField(max_length=2048)
    password = models.CharField(max_length=2048)
    
    class Meta:
        verbose_name_plural = "wims"



class LMS(models.Model):
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