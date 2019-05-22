# -*- coding: utf-8 -*-
#
#  config.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>


"""
Use this file to override settings declared in settings.py instead of
modifying the later to avoid conflict in case settings.py is modified in
the future.

To override a setting, just redeclare it here, it will prevail over the
one in settings.py.

In any case, you should at least override DEBUG to False, SECRET_KEY and ALLOWED_HOSTS.

You may also consider overriding CSRF_COOKIE_SECURE, SESSION_COOKIE_SECURE, DATABASES,
LOGGING, EMAIL_BACKEND and its related settings.

For more informations, see:
 - Django's settings | https://docs.djangoproject.com/en/2.1/ref/settings/
 - Deployment checklist | https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/
"""
