# -*- coding: utf-8 -*-
#
#  test_models.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>

from lti_app.models import GradeLinkExam, GradeLinkSheet
from lti_app.tests.utils import BaseGradeLinksViewTestCase



class GradeLinkSheetTestCase(BaseGradeLinksViewTestCase):
    
    def test_send_back_ok(self):
        gl = GradeLinkSheet.objects.create(user=self.user, sourcedid="1", url=self.url_ok,
                                           lms=self.lms1, activity=self.wsheet1)
        self.assertTrue(gl.send_back(1))
    
    
    def test_send_back_wrong_url(self):
        gl = GradeLinkSheet.objects.create(user=self.user, sourcedid="1", url="wrong",
                                           lms=self.lms1, activity=self.wsheet1)
        self.assertFalse(gl.send_back(1))
    
    
    def test_send_back_error(self):
        gl = GradeLinkSheet.objects.create(user=self.user, sourcedid="1", url=self.url_error,
                                           lms=self.lms1, activity=self.wsheet1)
        self.assertFalse(gl.send_back(1))
    
    
    def test_send_back_badly_formatted(self):
        gl = GradeLinkSheet.objects.create(user=self.user, sourcedid="1",
                                           url=self.url_badly_formatted, lms=self.lms1,
                                           activity=self.wsheet1)
        self.assertFalse(gl.send_back(1))
    
    
    def test_send_back_all(self):
        GradeLinkSheet.objects.create(user=self.user, sourcedid="1", url=self.url_ok,
                                      lms=self.lms1, activity=self.wsheet1)
        self.assertEqual(1, GradeLinkSheet.send_back_all(self.wsheet1))



class GradeLinkExamTestCase(BaseGradeLinksViewTestCase):
    
    def test_send_back_ok(self):
        gl = GradeLinkExam.objects.create(user=self.user, sourcedid="1", url=self.url_ok,
                                          lms=self.lms1, activity=self.wexam1)
        self.assertTrue(gl.send_back(1))
    
    
    def test_send_back_wrong_url(self):
        gl = GradeLinkExam.objects.create(user=self.user, sourcedid="1", url="wrong",
                                          lms=self.lms1, activity=self.wexam1)
        self.assertFalse(gl.send_back(1))
    
    
    def test_send_back_error(self):
        gl = GradeLinkExam.objects.create(user=self.user, sourcedid="1", url=self.url_error,
                                          lms=self.lms1, activity=self.wexam1)
        self.assertFalse(gl.send_back(1))
    
    
    def test_send_back_badly_formatted(self):
        gl = GradeLinkExam.objects.create(user=self.user, sourcedid="1",
                                          url=self.url_badly_formatted, lms=self.lms1,
                                          activity=self.wexam1)
        self.assertFalse(gl.send_back(1))
    
    
    def test_send_back_all(self):
        GradeLinkExam.objects.create(user=self.user, sourcedid="1", url=self.url_ok,
                                     lms=self.lms1, activity=self.wexam1)
        self.assertEqual(1, GradeLinkExam.send_back_all(self.wexam1))
