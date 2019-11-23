# -*- coding: utf-8 -*-
#
#  test_models.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
from lti_app.models import GradeLinkExam, GradeLinkSheet
from lti_app.tasks import send_back_all_exams_grades, send_back_all_sheets_grades
from lti_app.tests.utils import BaseGradeLinksViewTestCase



class TestTasks(BaseGradeLinksViewTestCase):
    
    def test_send_back_all_sheets_grades(self):
        GradeLinkSheet.objects.create(user=self.user, sourcedid="1", url=self.url_ok,
                                      lms=self.lms1, activity=self.wsheet1)
        self.assertEqual(1, send_back_all_sheets_grades())
    
    
    def test_send_back_all_exams_grades(self):
        GradeLinkExam.objects.create(user=self.user, sourcedid="1", url=self.url_ok,
                                     lms=self.lms1, activity=self.wexam1)
        self.assertEqual(1, send_back_all_exams_grades())
