# -*- coding: utf-8 -*-
#
#  utils.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import logging
import random
import string
from datetime import datetime
from string import ascii_letters, digits

import wimsapi
from django.conf import settings
from django.core.exceptions import PermissionDenied
from wimsapi import Sheet

from api.models import Activity, WimsClass, WimsUser
from lti_app.enums import Role


logger = logging.getLogger(__name__)



def create_supervisor(params):
    """Create an instance of wimapi.User corresponding to the class' supervisor with the given LTI
    request's parameters."""
    supervisor = {
        "quser":     "supervisor",
        "lastname":  (params['custom_supervisor_lastname']
                      or ("" if params['custom_supervisor_firstname'] else "Supervisor")),
        "firstname": params['custom_supervisor_firstname'] or "",
        "password":  ''.join(random.choice(ascii_letters + digits) for _ in range(20)),
        "email":     params["lis_person_contact_email_primary"],
    }
    return wimsapi.User(**supervisor)



def create_class(wims_srv, params):
    """Create an instance of wimsapi.Class with the given LTI request's parameters and wclass_db."""
    wclass_dic = {
        "name":        params["custom_class_name"] or params["context_title"],
        "institution": (params["custom_class_institution"]
                        or params["tool_consumer_instance_description"]),
        "email":       params["custom_class_email"] or params["lis_person_contact_email_primary"],
        "lang":        params["custom_class_lang"] or params["launch_presentation_locale"][:2],
        "expiration":  (params["custom_class_expiration"]
                        or (datetime.now() + wims_srv.expiration).strftime("%Y%m%d")),
        "limit":       params["custom_class_limit"] or wims_srv.class_limit,
        "level":       params["custom_class_level"] or "H4",
        "css":         params["custom_class_css"] or "",
        "password":    ''.join(random.choice(ascii_letters + digits) for _ in range(20)),
        "supervisor":  create_supervisor(params),
        "rclass":      wims_srv.rclass,
    }
    
    if params["custom_clone_class"] is not None:
        wapi = wimsapi.WimsAPI(wims_srv.url, wims_srv.ident, wims_srv.passwd)
        bol, response = wapi.copyclass(params["custom_clone_class"], wims_srv.rclass)
        if not bol:
            raise wimsapi.AdmRawError(response['message'])
        wclass = wimsapi.Class.get(wims_srv.url, wims_srv.ident, wims_srv.passwd,
                                   response['new_class'], wims_srv.rclass)
        for k, v in wclass_dic.items():
            if k == "css":
                continue
            setattr(wclass, k, v)
    else:
        wclass = wimsapi.Class(**wclass_dic)
    
    return wclass



def get_or_create_class(lms, wims_srv, wims, parameters):
    """Get the WIMS' class database and wimsapi.Class instances, create them if they does not
    exists.
    
    Raises:
        - exceptions.PermissionDenied if the class does not exists and none of the roles in
            the LTI request's parameters is in ROLES_ALLOWED_CREATE_WIMS_CLASS.
        - wimsapi.AdmRawError if the WIMS' server denied a request.
        - requests.RequestException if the WIMS server could not be joined.
    
    Returns a tuple (wclass_db, wclass) where wclas_db is an instance of models.WimsClass and
    wclass an instance of wimsapi.Class."""
    try:
        wclass_db = WimsClass.objects.get(wims=wims_srv, lms=lms,
                                          lms_uuid=parameters['context_id'])
        wclass = wimsapi.Class.get(wims.url, wims.ident, wims.passwd, wclass_db.qclass,
                                   wims_srv.rclass)
    
    except WimsClass.DoesNotExist:
        role = Role.parse_role_lti(parameters["roles"])
        if set(role).isdisjoint(settings.ROLES_ALLOWED_CREATE_WIMS_CLASS):
            logger.warning(str(role))
            msg = ("You must have at least one of these roles to create a Wims class: %s. Your "
                   "roles: %s")
            msg %= (str([r.value for r in settings.ROLES_ALLOWED_CREATE_WIMS_CLASS]),
                    str([r.value for r in role]))
            raise PermissionDenied(msg)
        
        wclass = create_class(wims_srv, parameters)
        wclass.save(wims.url, wims.ident, wims.passwd)
        wclass_db = WimsClass.objects.create(
            lms=lms, lms_uuid=parameters["context_id"],
            wims=wims_srv, qclass=wclass.qclass, name="test1"
        )
        logger.info("New class created (id : %d - wims id : %s - lms id : %s)"
                    % (wclass_db.id, str(wclass.qclass), str(wclass_db.lms_uuid)))
        WimsUser.objects.create(wclass=wclass_db, quser="supervisor")
        logger.info("New user created (wims id : supervisor - lms id : None) in class %d"
                    % wclass_db.id)
    
    return wclass_db, wclass



def create_user(parameters):
    """Create an instance of wimsapi.User with the given LTI request's parameters."""
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
    lastname = parameters['lis_person_name_family']
    firstname = parameters['lis_person_name_given']
    mail = parameters["lis_person_contact_email_primary"]
    quser = (firstname[0] + lastname).lower()
    
    return wimsapi.User(quser, lastname, firstname, password, mail,
                        regnum=parameters["user_id"])



def get_or_create_user(wclass_db, wclass, parameters):
    """Get the WIMS' user database and wimsapi.User instances, create them if they does not
    exists.
    
    If at least one of the roles in the LTI request's parameters is in
    ROLES_ALLOWED_CREATE_WIMS_CLASS, the user will be connected as supervisor.
    
    Raises:
        - wimsapi.AdmRawError if the WIMS' server denied a request.
        - requests.RequestException if the WIMS server could not be joined.
    
    Returns a tuple (user_db, user) where user_db is an instance of models.WimsUser and
    user an instance of wimsapi.User."""
    try:
        role = Role.parse_role_lti(parameters["roles"])
        if not set(role).isdisjoint(settings.ROLES_ALLOWED_CREATE_WIMS_CLASS):
            user_db = WimsUser.objects.get(lms_uuid=None, wclass=wclass_db)
        else:
            user_db = WimsUser.objects.get(lms_uuid=parameters['user_id'], wclass=wclass_db)
        user = wimsapi.User.get(wclass, user_db.quser)
    except WimsUser.DoesNotExist:
        user = create_user(parameters)
        
        i = 0
        while True:
            try:
                wclass.additem(user)
                break
            except wimsapi.AdmRawError as e:
                # Raised if an user with the same quser already exists,
                # in this case, keep trying by appending integer to quser (jdoe, jdoe1,
                # jdoe2, ...), stopping after 100 tries.
                
                # Can also be raised if an error occured while communicating with the
                # WIMS server, hence the following test.
                if "user already exists" not in str(e) or i >= 100:  # pragma: no cover
                    raise
                
                if i:
                    user.quser = user.quser[:-len(str(i))]
                i += 1
                user.quser += str(i)
        
        user_db = WimsUser.objects.create(
            lms_uuid=parameters["user_id"], wclass=wclass_db, quser=user.quser
        )
        logger.info("New user created (wims id: %s - lms id : %s) in class %d"
                    % (user.quser, str(user_db.lms_uuid), wclass_db.id))
    
    return user_db, user



def get_sheet(wclass_db, wclass, qsheet, parameters):
    """Get the WIMS' activity database and wimsapi.Sheet instances, create them if they does not
    exists.
    
    Raises:
        - wimsapi.AdmRawError if the WIMS' server denied a request.
        - requests.RequestException if the WIMS server could not be joined.
    
    Returns a tuple (activity_db, sheet) where activity_db is an instance of models.Activity and
    sheet an instance of wimsapi.Sheet."""
    
    sheet = wclass.getitem(qsheet, Sheet)
    try:
        activity = Activity.objects.get(wclass=wclass_db, qsheet=str(qsheet),
                                        lms_uuid=parameters["resource_link_id"])
    except Activity.DoesNotExist:
        activity = Activity.objects.create(
            lms_uuid=parameters["resource_link_id"],
            wclass=wclass_db, qsheet=str(qsheet)
        )
        logger.info("New sheet created (wims id: %s - lms id : %s) in class %d"
                    % (str(qsheet), str(activity.lms_uuid), wclass_db.id))
    
    return activity, sheet
