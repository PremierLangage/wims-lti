# Installation

## Dependencies

* Python 3.5+
* pip3
* Apache2 & mod_wsgi


First, you need to clone the repositoy:

```bash
git clone https://openproject.u-pem.fr/git/wims-lti.git
cd wims-lti
```
Then, you have to edit `wimsLTI/config.py` to change some default parameters, 
see [Parameters reference](https://docs.djangoproject.com/fr/2.1/ref/settings/).
First, it's important to set `DEBUG = False` and to modify:
[`SECRET_KEY`](https://docs.djangoproject.com/fr/2.1/ref/settings/#std:setting-SECRET_KEY) et
[`ALLOWED_HOSTS`](https://docs.djangoproject.com/fr/2.1/ref/settings/#allowed-hosts).

Once parameter correctly defined, then launch the installation script.
It will ask for a user name, an email address, and a password to create
an administration account.

***Careful: If you are using a [python environment](https://docs.python.org/fr/3/tutorial/venv.html),
remember to use it.***

```bash
./install.sh
```

Now, you only have to configure *Apache*,
see [the documentation](https://docs.djangoproject.com/fr/2.1/howto/deployment/wsgi/modwsgi/).

## Configuration

### WIMS side

In order to have the *WIMS* server to accept **WIMS-LTI** requests, you have to create
a connection file. The creation of this file is explained 
[here](https://wimsapi.readthedocs.io/#configuration)

It is important to add the IP address of the **WIMS-LTI gateway** to the 
`ident_site` key and not the ip of the *LMS*
Remember the value of the `ident_password` and the name of the created file,
you will need these to add the server to **WIMS-LTI**.


### WIMS-LTI side

1. Connect to `[WIMS-LTI SERVEUR]/admin/` and enter the administration 
account login and password that you got when you installed the server.

2. Click on `wims` (or go to `[WIMS-LTI SERVEUR]/admin/wims/wims/`)

3. Click `ADD WIMS` in the top left, and fill the form:
    * `DNS` : DNS of the *WIMS* server, ex: `wims.unice.fr`.
    * `URL` : URL of the *WIMS* server CGI, ex: `https://wims.unice.fr/wims/wims.cgi`.
    * `Name` : Name to identify the *WIMS* server, ex: `WIMS UNICE`.
    * `Ident` : Name of the connection file created on the *WIMS* server. 
                For example, if the file created was `[WIMS_HOME]/log/classes/.connections/myself`,
                enter `myself`.
    * `Passwd` : Value of the key `ident_password` of the configuration file *Ident*.
    * `Rclass` : Identifiers used by *WIMS-LTI* to create classes on the *WIMS* server,
                 for example: `myclass`.
    
    Repeat ***3.*** for each *WIMS* server that you want to add.

4. Go back to `[WIMS-LTI SERVEUR]/admin/` and click on `LMS` (or go to 
`[WIMS-LTI SERVEUR]/admin/wims/lms/`)

5. Click `ADD LMS` in the top left and fill the form:
    * `UUID` : UUID of the *LMS* corresponding to the `tool_consumer_instance_guid` parameter
               of the LTI request. Most of the time, it is the DNS of the *LMS*.
               For example: `elearning.u-pem.fr`
    * `Name` : Name that identifies the *LMS*, for example: `Moodle UPEM`.
    * `URL` : URL of the *LMS*, for example: `https://elearning.u-pem.fr/`
    
    Repeat ***5.*** for each *LMS* that you want to add.


___

It is now possible to connect to any *WIMS* server added, from any *LMS* added, thanks to the URLs.

* `[WIMS-LTI SERVEUR]/dns/[WIMS DNS]/` -
  for example : `https://wims-lti.u-pem.fr/dns/wims.u-pem.fr/`

ou

* `[WIMS-LTI SERVEUR]/dns/[WIMS ID]/` - where `WIMS ID` is the ID of the *WIMS* server
  in the **WIMS-LTI** database,
  for example : `https://wims-lti.u-pem.fr/id/0/`

The list of the URLs can be found on the page `[WIMS-LTI SERVEUR]/list/`
