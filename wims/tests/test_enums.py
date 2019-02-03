from unittest import mock

from django.test import TestCase

from wims.enums import Role



class RoleTestCase(TestCase):
    
    def test_parse_role_lti_label(self):
        self.assertEqual([Role.STUDENT], Role.parse_role_lti("Student"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI], Role.parse_role_lti("Student, Alumni"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI], Role.parse_role_lti("Student ,Alumni"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI], Role.parse_role_lti("Student,Alumni"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI], Role.parse_role_lti(" Student , Alumni "))
    
    
    def test_parse_role_lti_URN(self):
        self.assertEqual([Role.STUDENT], Role.parse_role_lti("urn:lti:instrole:ims/lis/Student"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI],
                         Role.parse_role_lti("urn:lti:instrole:ims/lis/Student, "
                                             "urn:lti:instrole:ims/lis/Alumni"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI],
                         Role.parse_role_lti("urn:lti:instrole:ims/lis/Student ,"
                                             "urn:lti:instrole:ims/lis/Alumni"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI],
                         Role.parse_role_lti("urn:lti:instrole:ims/lis/Student,"
                                             "urn:lti:instrole:ims/lis/Alumni"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI],
                         Role.parse_role_lti(" urn:lti:instrole:ims/lis/Student , "
                                             "urn:lti:instrole:ims/lis/Alumni "))
    
    
    def test_parse_role_lti_label_URN(self):
        self.assertEqual([Role.STUDENT, Role.ALUMNI],
                         Role.parse_role_lti("urn:lti:instrole:ims/lis/Student, "
                                             "Alumni"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI],
                         Role.parse_role_lti("urn:lti:instrole:ims/lis/Student ,"
                                             "Alumni"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI],
                         Role.parse_role_lti("urn:lti:instrole:ims/lis/Student,"
                                             "Alumni"))
        self.assertEqual([Role.STUDENT, Role.ALUMNI],
                         Role.parse_role_lti(" urn:lti:instrole:ims/lis/Student , "
                                             "Alumni "))
    
    
    @mock.patch("wims.enums.logger")
    def test_parse_role_unkown_one(self, logger):
        self.assertEqual([], Role.parse_role_lti("Unknown"))
        logger.warning.assert_called_with("Received unknown LTI role: 'Unknown'")
    
    
    @mock.patch("wims.enums.logger")
    def test_parse_role_unkown_multiple(self, logger):
        self.assertEqual([Role.STUDENT, Role.ALUMNI],
                         Role.parse_role_lti("Student, Unknown1, Unknown2, Alumni"))
        logger.warning.assert_has_calls([
            mock.call("Received unknown LTI role: 'Unknown1'"),
            mock.call("Received unknown LTI role: 'Unknown2'"),
        ])
