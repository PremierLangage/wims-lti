"""
WSGI config for wimsLTI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application


path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wimsLTI.settings')

application = get_wsgi_application()
