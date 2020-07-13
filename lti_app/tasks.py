# -*- coding: utf-8 -*-
#
#  stasks.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>

import logging
import traceback

import wimsapi
from django.apps import apps

from wimsLTI import settings


logger = logging.getLogger(__name__)



def send_back_all_sheets_grades() -> int:
    """Send back the grades of every User of every WimsSheet to their corresponding LMS."""
    GradeLinkSheet = apps.get_model("lti_app", "GradeLinkSheet")
    WimsSheet = apps.get_model("lti_app", "WimsSheet")
    total = 0
    
    logger.info("Sending grades of every User of every WimsSheet to their LMS")
    for sheet in WimsSheet.objects.all():
        try:
            total = + GradeLinkSheet.send_back_all(sheet)
        except wimsapi.WimsAPIError:  # pragma: no cover
            logger.info("Failed to send grade for sheet '%s'" % str(sheet))
            logger.info(traceback.format_exc())
    logger.info("Done sending grades of every User of every WimsSheet to their LMS (%d sent)"
                % total)
    return total



def send_back_all_exams_grades() -> int:
    """Send back the grades of every User of every WimsExam to their corresponding LMS."""
    GradeLinkExam = apps.get_model("lti_app", "GradeLinkExam")
    WimsExam = apps.get_model("lti_app", "WimsExam")
    total = 0
    
    logger.info("Sending grades of every User of every WimsExam to their LMS")
    for exam in WimsExam.objects.all():
        try:
            total = + GradeLinkExam.send_back_all(exam)
        except wimsapi.WimsAPIError:  # pragma: no cover
            logger.info("Failed to send grade for exam '%s'" % str(exam))
            logger.info(traceback.format_exc())
    logger.info("Done sending grades of every User of every WimsExam to their LMS (%d sent)"
                % total)
    return total



def check_classes_exists() -> int:
    """Checks that the corresponding class exists on its WIMS server for every WimsClass. Delete
    the instance of WimsClass if not."""
    WimsClass = apps.get_model("lti_app", "WimsClass")
    
    deleted = 0
    for c in WimsClass.objects.all():
        try:
            wimsapi.Class.get(
                c.wims.url, c.wims.ident, c.wims.passwd, c.qclass, c.wims.rclass,
                timeout=settings.WIMSAPI_TIMEOUT
            )
        except wimsapi.WimsAPIError as e:
            # Delete the class if it does not exists on the server anymore
            if "class %s not existing" % str(c.qclass) in str(e):
                logger.info(
                    (
                        "Deleting class of pk '%s' has the corresponding class of id '%s' does not "
                        "exists on the WIMS server '%s'  anymore")
                    % (str(c.pk), str(c.qclass), c.wims.url)
                )
                c.delete()
                deleted += 1
            else:  # pragma: no cover
                logger.info(
                    "An error occurred checking for class of pk '%s' (qclass '%s', server '%s')"
                    % (str(c.pk), str(c.qclass), c.wims.url)
                )
                logger.info(traceback.format_exc())
    
    return deleted
