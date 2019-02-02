# -*- coding: utf-8 -*-
#
#  enums.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging
from enum import Enum


logger = logging.getLogger(__name__)



class Role(Enum):
    """Used by .models.Profile to define the user's role."""
    STUDENT = 0
    FACULTY = 1
    MEMBER = 2
    LEARNER = 3
    INSTRUCTOR = 4
    MENTOR = 5
    STAFF = 6
    ALUMNI = 7
    PROSPECTIVESTUDENT = 8
    CONTENTDEVELOPPER = 9
    GUEST = 10
    OTHER = 11
    ADMINISTRATOR = 12
    OBSERVER = 13
    NONE = 14
    
    LABEL = {
        "Student":            STUDENT,
        "Faculty":            FACULTY,
        "Member":             MEMBER,
        "Learner":            LEARNER,
        "Instructor":         INSTRUCTOR,
        "Mentor":             MENTOR,
        "Staff":              STAFF,
        "Alumni":             ALUMNI,
        "ProspectiveStudent": PROSPECTIVESTUDENT,
        "ContentDeveloper":   CONTENTDEVELOPPER,
        "Guest":              GUEST,
        "Other":              OTHER,
        "Administrator":      ADMINISTRATOR,
        "Observer":           OBSERVER,
        "None":               NONE,
    }
    
    URN = {
        "urn:lti:instrole:ims/lis/Student":            STUDENT,
        "urn:lti:instrole:ims/lis/Faculty":            FACULTY,
        "urn:lti:instrole:ims/lis/Member":             MEMBER,
        "urn:lti:instrole:ims/lis/Learner":            LEARNER,
        "urn:lti:instrole:ims/lis/Instructor":         INSTRUCTOR,
        "urn:lti:instrole:ims/lis/Mentor":             MENTOR,
        "urn:lti:instrole:ims/lis/Staff":              STAFF,
        "urn:lti:instrole:ims/lis/Alumni":             ALUMNI,
        "urn:lti:instrole:ims/lis/ProspectiveStudent": PROSPECTIVESTUDENT,
        "urn:lti:instrole:ims/lis/Guest":              GUEST,
        "urn:lti:instrole:ims/lis/Other":              OTHER,
        "urn:lti:instrole:ims/lis/Administrator":      ADMINISTRATOR,
        "urn:lti:insitertrole:ims/lis/Observer":       OBSERVER,
        "urn:lti:instrole:ims/lis/None":               NONE,
        "urn:lti:role:ims/lis/ContentDeveloper":       CONTENTDEVELOPPER,
    }
    
    
    @classmethod
    def parse_role_lti(cls, role):
        """Returns the list of Roles' enums corresponding to the LTI roles.
    
            Parameter:
                role - (str) The role string retrieved from the LTI request."""
        ret = []
        for r in [r.strip().title() if ":" in r else r.strip() for r in role.split(",")]:
            if ":" in r and r in cls.URN:
                ret.append(cls.URN[r])
            elif r in cls.LABEL:
                ret.append(cls.LABEL[r])
            else:
                logger.warning("Received unknown LTI role: '%s'" % r)
        
        return ret
