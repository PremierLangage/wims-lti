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
    STUDENT = "Student"
    FACULTY = "Faculty"
    MEMBER = "Member"
    LEARNER = "Learner"
    INSTRUCTOR = "Instructor"
    MENTOR = "Mentor"
    STAFF = "Staff"
    ALUMNI = "Alumni"
    PROSPECTIVESTUDENT = "Prospectivestudent"
    CONTENTDEVELOPPER = "Contentdevelopper"
    GUEST = "Guest"
    OTHER = "Other"
    ADMINISTRATOR = "Administrator"
    OBSERVER = "Observer"
    NONE = "None"
    
    
    @classmethod
    def parse_role_lti(cls, role):
        """Returns the list of Roles' enums corresponding to the LTI roles.
    
            Parameter:
                role - (str) The role string retrieved from the LTI request."""
        ret = []
        roles = [
            r.replace("urn:lti:instrole:ims/lis/", "") \
             .replace("urn:lti:sysrole:ims/lis/", "") \
             .replace("urn:lti:role:ims/lis/", "") \
             .strip()
            for r in role.split(",")
        ]
        roles = [r.replace("urn:lti:instrole:ims/lis/", "") for r in roles]
        for r in [r.replace("urn:lti:instrole:ims/lis/", "").strip() for r in role.split(",")]:
            try:
                ret.append(Role(r.title()))
            except ValueError:
                logger.warning("Received unknown LTI role: '%s'" % r)
        
        return ret
