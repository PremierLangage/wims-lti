import os, sys
sys.path.append(os.path.realpath(os.path.join(__file__, '../../../')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "serverpl.settings")

import django
django.setup()

from django.contrib.auth.models import User
from lti_app.models import LMS, WIMS


# Create admin
try :
    user = User.objects.create_user(username='admin', password='adminadmin')
    user.is_staff = True
    user.is_admin = True
    user.is_superuser = True
    user.save()
except django.db.utils.IntegrityError:
    print("User 'admin' already created")
    user = User.objects.get(username='admin')

try:
    lms = LMS.objects.create(uuid="elearning.u-pem.fr", name="Moodle UPEM", url="https://elearning.u-pem.fr",
                             key="wimslti", secret="password")
except django.db.utils.IntegrityError:
    lms = LMS.objects.get(uuid="elearning.u-pem.fr")
    print("LMS 'Moodle UPEM' already created")

try:
    wims = WIMS.objects.create(name="WIMS UPEM", url="http://pl-test.u-pem.fr:7777/wims/wims.cgi",
                               ident="myself", passwd="toto", rclass="myclass")
    wims.allowed_lms.add(lms)
except:
    wims = WIMS.objects.get(name="WIMS UPEM")
    print("WIMS 'WIMS UPEM' already created")
