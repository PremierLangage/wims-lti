# Installation

## Dependencies

* git
* Python 3.5+
* pip3
* Apache2 & mod_wsgi


## Downloading

You can clone the server from github:

```bash
git clone https://openproject.u-pem.fr/git/wims-lti.git
cd wims-lti
```

## Configuration of WIMS-LTI

You must edit `wimsLTI/config.py` to change some default parameters, 
see [Parameters reference](https://docs.djangoproject.com/en/2.2/ref/settings/).  
You should especially look at:

* [*DEBUG*](https://docs.djangoproject.com/en/2.2/ref/settings/#debug)
* [*SECRET_KEY*](https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key)
* [*ALLOWED_HOSTS*](https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts)
* [*ADMINS*](https://docs.djangoproject.com/fr/2.2/ref/settings/#admins)
* [*EMAIL_HOST*](https://docs.djangoproject.com/en/2.2/ref/settings/#email-host) 
and [*SERVER_EMAIL*](https://docs.djangoproject.com/en/2.2/ref/settings/#server-email)
* [*DATABASES*](https://docs.djangoproject.com/fr/2.2/ref/settings/#databases) - If 
you want to use something else than sqlite (see `wimsLTI/settings.py` for the default value).


Once the parameters are correctly defined, launch the installation script (`install.sh`).
It will ask for a user name, an email address, and a password to create
an administration account.


## Configuration of Apache2

Now, you only have to configure *Apache*,
see [the documentation](https://docs.djangoproject.com/fr/2.1/howto/deployment/wsgi/modwsgi/).
Here an example of such conf:


```text
<VirtualHost *:443>
    ServerName wims-lti.u-pem.fr
        
    Use SSL

    Alias /static /path/to/wims-lti/static/
    <Directory /path/to/wims-lti/static/>
        Require all granted
    </Directory>

    <Directory /path/to/wims-lti/wimsLTI/>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    SetEnv PYTHONIOENCODING utf-8
    WSGIDaemonProcess wims-lti python-path=/path/to/wims-lti/wimsLTI/
    WSGIProcessGroup  wims-lti
    WSGIScriptAlias / /path/to/wims-lti/wimsLTI/wsgi.py
</VirtualHost>
```
