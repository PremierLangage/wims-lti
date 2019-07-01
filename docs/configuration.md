# Configuration

Once the server has been correctly installed, you must add *LMS*'s and *WIMS* servers on
*WIMS-LTI* through the Administration Panel. To add *WIMS* servers, your must first configure
it to accept **WIMS-LTI** requests.

## WIMS

In order for a *WIMS* server to accept **WIMS-LTI** requests, you have to create
a connection file. The creation of this file is explained 
[here](https://wimsapi.readthedocs.io/#configuration).

It is important to add the IP address of the **WIMS-LTI server** to the 
`ident_site` key and not the IP of the *LMS*.
Remember the value of the `ident_password` and the name of the created file,
you will need these to add the server to **WIMS-LTI**.


## WIMS-LTI

1. Go to the administration panel by connecting to `[WIMS-LTI SERVEUR]/admin/` and
enter the administration account login and password that you entered when you installed
the server (you can create a new one by running `python3 manage.py createsuperuser`).

2. Click on `LMS` (or go to  `[WIMS-LTI SERVEUR]/admin/lti_app/lms/`)

3. Click `ADD LMS` in the top left and fill the form:
    * `GUID` : GUID of the *LMS* corresponding to the `tool_consumer_instance_guid` parameter
               of the LTI request. Most of the time, it is the DNS of the *LMS*.
               For example: `elearning.u-pem.fr`. [See below](#get-your-lms-guid) for a way to retrieve get your GUID.
    * `Name` : Name that identifies the *LMS*, for example: `Moodle UPEM`.
    * `URL` : URL of the *LMS*, for example: `https://elearning.u-pem.fr/`
    * `key`: Key that you'll need to enter on the LMS when creating a LTI activity.
    * `secret`: Secret that you'll need to enter on the LMS when creating a LTI activity.
    
*Repeat ***3.*** for each *LMS* that you want to add.*


4. Go back to `[WIMS-LTI SERVEUR]/admin/` and click on `wims` (or go to `[WIMS-LTI SERVEUR]/admin/lti_app/wims/`)

5. Click `ADD WIMS` in the top left, and fill the form:
    * `Name` : Name to identify the *WIMS* server, ex: `WIMS UPEM`.
    * `URL` : URL of the *WIMS* server CGI, ex: `https://wims.u-pem.fr/wims/wims.cgi`.
    * `Ident` : Name of the connection file created on the *WIMS* server. 
                For example, if the file created was `[WIMS_HOME]/log/classes/.connections/myself`,
                enter `myself`.
    * `Passwd` : Value of the key `ident_password` of the configuration file *Ident*.
    * `Rclass` : Identifiers used by *WIMS-LTI* to create classes on the *WIMS* server,
                 for example: `myclass`.
    * `Allowed LMS` : Select the LMS allowed to connect to this WIMS server (use CTRL + click to 
      select more than one).
    
*Repeat ***5.*** for each *WIMS* server that you want to add.*


### Get your LMS' GUID

If you cannot find the *GUID* of your *LMS*, and if *LTI* is enable, a good way to get it is
to create an *LTI* activity with the following parameters:

* URL : `https://www.tsugi.org/lti-test/tool.php`
* Key : `12345`
* Secret : `secret`

The activity will redirect you on a webpage displaying the value of each *LTI* parameters,
including `tool_consumer_instance_guid`, which correspond to your *LMS' GUID*.