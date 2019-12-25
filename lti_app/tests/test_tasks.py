# -*- coding: utf-8 -*-
#
#  test_models.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>


from lti_app import tasks
from lti_app.models import GradeLinkExam, GradeLinkSheet, WimsClass
from lti_app.tests.utils import BaseGradeLinksViewTestCase



class TestTasks(BaseGradeLinksViewTestCase):
    
    def test_send_back_all_sheets_grades(self):
        GradeLinkSheet.objects.create(user=self.user, sourcedid="1", url=self.url_ok,
                                      lms=self.lms1, activity=self.wsheet1)
        self.assertEqual(1, tasks.send_back_all_sheets_grades())
    
    
    def test_send_back_all_exams_grades(self):
        GradeLinkExam.objects.create(user=self.user, sourcedid="1", url=self.url_ok,
                                     lms=self.lms1, activity=self.wexam1)
        self.assertEqual(1, tasks.send_back_all_exams_grades())
    
    
    def test_check_classes_exists(self):
        WimsClass.objects.create(
            lms=self.lms1, lms_guid="1337", wims=self.wims2, qclass="1337", name="test1"
        )
        WimsClass.objects.create(
            lms=self.lms1, lms_guid="1338", wims=self.wims2, qclass="1338", name="test1"
        )
        WimsClass.objects.create(
            lms=self.lms1, lms_guid="1339", wims=self.wims2, qclass="1339", name="test1"
        )
        
        before = WimsClass.objects.all().count()
        self.assertEqual(3, tasks.check_classes_exists())
        self.assertEqual(before - 3, WimsClass.objects.all().count())
