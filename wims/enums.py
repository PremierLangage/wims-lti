# -*- coding: utf-8 -*-
#
#  enums.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#


from enum import auto

from enumfields import Enum



class Role(Enum):
    """Used by .models.Profile to define the user's role."""
    STUDENT = auto()
    FACULTY = auto()
    MEMBER = auto()
    LEARNER = auto()
    INSTRUCTOR = auto()
    MENTOR = auto()
    STAFF = auto()
    ALUMNI = auto()
    PROSPECTIVESTUDENT = auto()
    GUEST = auto()
    OTHER = auto()
    ADMINISTRATOR = auto()
    OBSERVER = auto()
    NONE = auto()
    
    
    class Label:
        """Label used by the Django Administration Interface.
        
        Correspond to roles handles definied by LIS standard."""
        STUDENT = "Student"
        FACULTY = "Faculty"
        MEMBER = "Member"
        LEARNER = "Learner"
        INSTRUCTOR = "Instructor"
        MENTOR = "Mentor"
        STAFF = "Staff"
        ALUMNI = "Alumni"
        PROSPECTIVESTUDENT = "Prospectivestudent"
        GUEST = "Guest"
        OTHER = "Other"
        ADMINISTRATOR = "Administrator"
        OBSERVER = "Observer"
        NONE = "None"
    
    
    class URN:
        """URN values for institution roles as defined by the LIS standard."""
        STUDENT = "urn:lti:instrole:ims/lis/Student"
        FACULTY = "urn:lti:instrole:ims/lis/Faculty"
        MEMBER = "urn:lti:instrole:ims/lis/Member"
        LEARNER = "urn:lti:instrole:ims/lis/Learner"
        INSTRUCTOR = "urn:lti:instrole:ims/lis/Instructor"
        MENTOR = "urn:lti:instrole:ims/lis/Mentor"
        STAFF = "urn:lti:instrole:ims/lis/Staff"
        ALUMNI = "urn:lti:instrole:ims/lis/Alumni"
        PROSPECTIVESTUDENT = "urn:lti:instrole:ims/lis/ProspectiveStudent"
        GUEST = "urn:lti:instrole:ims/lis/Guest"
        OTHER = "urn:lti:instrole:ims/lis/Other"
        ADMINISTRATOR = "urn:lti:instrole:ims/lis/Administrator"
        OBSERVER = "urn:lti:insitertrole:ims/lis/Observer"
        NONE = "urn:lti:instrole:ims/lis/None"
        CONTENTDEVELOPPER = "urn:lti:role:ims/lis/ContentDeveloper"
    
    
    @classmethod
    def map_label(cls):
        """Returns a dictionnary mapping label to their corresponding enum."""
        return {r.label: r for r in iter(Role)}
    
    
    @classmethod
    def map_urn(cls):
        """Returns a dictionnary mapping URN to their corresponding enum."""
        return {r.urn: r for r in iter(Role)}
    
    
    @staticmethod
    def parse_role_lti(role):
        """Returns the list of Roles' enums corresponding to the LTI roles.

        Parameter:
            role - (str) The role string retrieved from the LTI request."""
        urn, label = Role.map_urn(), Role.map_label()
        
        ret = []
        for r in [r.split().title() if ":" in r else r.split() for r in role.split(",")]:
            if ":" in r and r in urn:
                ret.append(urn[r])
            elif r in label:
                ret.append(label[r])
