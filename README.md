[![Build Status](https://travis-ci.org/PremierLangage/wims-lti.svg?branch=master)](https://travis-ci.org/PremierLangage/wims-lti)
[![codecov](https://codecov.io/gh/PremierLangage/wims-lti/branch/master/graph/badge.svg)](https://codecov.io/gh/PremierLangage/wims-lti)
[![GPLv3](https://img.shields.io/badge/license-GPLv3-brightgreen.svg)](#)


# WIMS-LTI

**WIMS-LTI** is a proxy server between a LMS and a WIMS using the LTI standard.  
The complete documention is available here : https://wims-lti.readthedocs.io/



# Introduction

**WIMS-LTI** is a gateway server that links a LMS to a WIMS server, using LTI.

**WIMS-LTI** allows :

* To create a WIMS class associated to a LMS' course.
* To create students corresponding to that course in the WIMS class.
* The students to connect to the WIMS server from the LMS.
* The teachers to connect to the WIMS class as supervisor or as students.
* To send the grades of students back to the LMS.


## How does it work ?

Once **WIMS-LTI** is installed and running, it is possible to add LMS and WIMS server
from the administration panel, each WIMS server having a list of authorized LMS.

Teacher will then be able to go on `[server]/lti/links/` to get the URL that should be
paste on the LMS.

There is two kinds of URL:

* Class URL : Create a new class and redirect to the class' home on WIMS the first time it is
    clicked on from a LMS, only redirect to the class' home on subsequent click. It will also create
    a corresponding user on the WIMS user if needed.
* Activity URL : Will redirect an user to the corresponding worksheet, creating the user if needed.
    If someone with a role of Teacher click on this link, it will also send every grade of the
    corresponding sheet to the LMS.
