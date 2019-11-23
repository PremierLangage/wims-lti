# -*- coding: utf-8 -*-
#
#  stasks.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>

import logging

from django.apps import apps


logger = logging.getLogger(__name__)



def send_back_all_sheets_grades() -> int:
    """Send back the grades of every User of every WimsSheet to their corresponding LMS."""
    GradeLinkSheet = apps.get_model("lti_app", "GradeLinkSheet")
    WimsSheet = apps.get_model("lti_app", "WimsSheet")
    total = 0
    
    logger.info("Sending grades of every User of every WimsSheet to their LMS")
    for sheet in WimsSheet.objects.all():
        total = + GradeLinkSheet.send_back_all(sheet)
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
        total = + GradeLinkExam.send_back_all(exam)
    logger.info("Done sending grades of every User of every WimsExam to their LMS (%d sent)"
                % total)
    return total
