# Usage

## WIMS

In order to have the *WIMS* server to accept **WIMS-LTI** requests, you have to create
a connection file. The creation of this file is explained 
[here](https://wimsapi.readthedocs.io/#configuration).

It is important to add the IP address of the **WIMS-LTI server** to the 
`ident_site` key and not the IP of the *LMS*.
Remember the value of the `ident_password` and the name of the created file,
you will need these to add the server to **WIMS-LTI**.


## WIMS-LTI

1. Connect to `[WIMS-LTI SERVEUR]/admin/` and enter the administration 
account login and password that you entered when you installed the server.

2. Click on `LMS` (or go to  `[WIMS-LTI SERVEUR]/admin/api/lms/`)

3. Click `ADD LMS` in the top left and fill the form:
    * `UUID` : UUID of the *LMS* corresponding to the `tool_consumer_instance_guid` parameter
               of the LTI request. Most of the time, it is the DNS of the *LMS*.
               For example: `elearning.u-pem.fr`
    * `Name` : Name that identifies the *LMS*, for example: `Moodle UPEM`.
    * `URL` : URL of the *LMS*, for example: `https://elearning.u-pem.fr/`
    * `key`: Key that you'll need to enter on the LMS when creating an LTI activity.
    * `secret`: Secret that you'll need to enter on the LMS when creating an LTI activity.
    
*Repeat ***3.*** for each *LMS* that you want to add.*


4. Go back to `[WIMS-LTI SERVEUR]/admin/` and click on `wims` (or go to `[WIMS-LTI SERVEUR]/admin/api/wims/`)

5. Click `ADD WIMS` in the top left, and fill the form:
    * `Name` : Name to identify the *WIMS* server, ex: `WIMS UPEM`.
    * `URL` : URL of the *WIMS* server CGI, ex: `https://wims.u-pem.fr/wims/wims.cgi`.
    * `Ident` : Name of the connection file created on the *WIMS* server. 
                For example, if the file created was `[WIMS_HOME]/log/classes/.connections/myself`,
                enter `myself`.
    * `Passwd` : Value of the key `ident_password` of the configuration file *Ident*.
    * `Rclass` : Identifiers used by *WIMS-LTI* to create classes on the *WIMS* server,
                 for example: `myclass`.
    * `Allowed LMS` : Select the LMS allowed to connect to this WIMS server.
    
*Repeat ***5.*** for each *WIMS* server that you want to add.*


## LTI URL

Teachers can go `[WIMS-LTI SERVEUR]/lti/links/`, search for their LMS, and copy
the link of the WIMS server the want to create a class on.
If they want to create a link to a worksheet (to send the grade back to the LMS),
they'll have to select the corresponding class, provide its password (sent
by email at the class' creation) and copy the URL corresponding to the worksheet
they want?
