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

from apscheduler.triggers.cron import CronTrigger


#  A boolean that turns on/off debug mode.
# Never deploy a site into production with DEBUG turned on.
# See https://docs.djangoproject.com/en/2.1/ref/settings/#debug
DEBUG = True

# A secret key for a particular Django installation. This is used to provide cryptographic signing,
# and should be set to a unique, unpredictable value.
# See https://docs.djangoproject.com/en/2.1/ref/settings/#secret-key
SECRET_KEY = '-qj!o^8$@!&7))^77^z8(-5rp*5x=7q(736)05x$h(inkfm^1#'

#  A list of strings representing the host/domain names that this Django site can serve. This is a
# security measure to prevent HTTP Host header attacks, which are possible even under many
# seemingly-safe web server configurations.

#  When DEBUG is True and ALLOWED_HOSTS is empty, the host is validated against
# ['localhost', '127.0.0.1', '[::1]'].
# See https://docs.djangoproject.com/en/2.1/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Port to use for the SMTP server defined in EMAIL_HOST.
EMAIL_PORT = 25
# The host to use for sending email.
EMAIL_HOST = "localhost"
# The email address that error messages come from, such as those sent to ADMINS and MANAGERS.
SERVER_EMAIL = "root@localhost"

# A list of all the people who get code error notifications. When DEBUG=False and AdminEmailHandler
# is configured in LOGGING (done by default), Django emails these people the details of
# exceptions raised in the request/response cycle.

# Each item in the list should be a tuple of (Full name, email address) Example:
# [('John', 'john@example.com'), ('Mary', 'mary@example.com')]
ADMINS = []

# The CronTrigger triggering the job sending every grade of the WIMS server to the LMS, see
# https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html for more information.
SEND_GRADE_BACK_CRON_TRIGGER = CronTrigger(
    year="*",
    month="*",
    day="*",
    week="*",
    day_of_week="*",
    hour="7,19",
    minute="0",
    second="0",
)

# The CronTrigger triggering the job checking that for every class registered on wims-lti, the
# corresponding class exists on its WIMS server, deleting the instance on wims-lti if not, see
# # https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html for more information.
CHECK_CLASSES_EXISTS_CRON_TRIGGER = CronTrigger(
    year="*",
    month="*",
    day="*",
    week="*",
    day_of_week="*",
    hour="7,19",
    minute="0",
    second="0",
)

# Time before requests sent to a WIMS server from wims-lti time out. Should be increased
# if some WIMS server contains a lot of classes / users.
WIMSAPI_TIMEOUT = 1
