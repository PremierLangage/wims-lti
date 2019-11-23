# -*- coding: utf-8 -*-
#
#  converters.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import warnings

from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from django.conf import settings

from lti_app.tasks import send_back_all_exams_grades, send_back_all_sheets_grades



def display_warnings():
    """Display warning for missing settings"""
    if settings.DEBUG:
        warnings.warn(
            "Settings 'DEBUG' has not been redefined in wimsLTI/config.py, "
            "see https://docs.djangoproject.com/fr/2.2/ref/settings/#debug",
            Warning
        )
    
    if settings.SECRET_KEY == '-qj!o^8$@!&7))^77^z8(-5rp*5x=7q(736)05x$h(inkfm^1#':
        warnings.warn(
            "Settings 'SECRET_KEY' has not been redefined in wimsLTI/config.py, "
            "see https://docs.djangoproject.com/fr/2.2/ref/settings/#secret-key",
            Warning
        )
    
    if settings.SERVER_EMAIL == "root@localhost":
        warnings.warn(
            "Settings 'SERVER_EMAIL' has not been redefined in wimsLTI/config.py, "
            "see https://docs.djangoproject.com/fr/2.2/ref/settings/#server-email",
            Warning
        )
    
    if settings.EMAIL_HOST == "localhost":
        warnings.warn(
            "Settings 'EMAIL_HOST' has not been redefined in wimsLTI/config.py, "
            "see https://docs.djangoproject.com/fr/2.2/ref/settings/#email-host",
            Warning
        )
    
    if not settings.ADMINS:
        warnings.warn(
            "Settings 'ADMINS' has not been redefined in wimsLTI/config.py, "
            "see https://docs.djangoproject.com/fr/2.2/ref/settings/#admins",
            Warning
        )



class LtiAppConfig(AppConfig):
    name = 'lti_app'
    
    
    def ready(self):
        """Display warning for missing settings and set up scheduled tasks."""
        
        display_warnings()
        
        scheduler = BackgroundScheduler(job_defaults={
            'coalesce':           True,
            'max_instances':      1,
            'misfire_grace_time': 60 * 10,
        })
        scheduler.add_job(send_back_all_sheets_grades,
                          trigger=settings.SEND_GRADE_BACK_CRON_TRIGGER)
        scheduler.add_job(send_back_all_exams_grades,
                          trigger=settings.SEND_GRADE_BACK_CRON_TRIGGER)
        scheduler.start()
