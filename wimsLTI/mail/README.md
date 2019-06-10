This directory contains the email title and body used when
sending the credentials of a WIMS class.

Each directory must be named according to the ISO 3166-1 country code.
These directory must contains two files : `title.txt`, corresponding
to the title of the mail, and `body.html` to the body of the mail.

Here an example of the directory structure:

```text
mail/
├── fr/
│   ├── title.txt
│   └── body.txt
├── en/
│   ├── title.txt
│   └── body.txt
...
```

In both of these field, it is possible to use variables corresponding to
the fields of the newly created WIMS class. You can use these fields by
putting them between curly bracket : `{field}`. Available fields are :

* `qclass` - ID of the class on WIMS.
* `name` - Name of the class.
* `institution` - Institution related to the class.
* `email` - Email address of the class.
* `class_password` - Password of the class.
* `supervisor_password` - Password of the supervisor.
* `lang` - Language of the class.
* `expiration` - Expiration date of the class in the format `yymmdd`.
* `limit` - Maximum number of student in the class.
* `level` - Level of the class (E1, E2, ..., E6, H1, ..., H6, U1, ..., U5, G, R).
* `lms_url` - URL of the LMS the LTI request has been sent from
* `wims_url` - URL of the WIMS server targeted by the LTI request
When creating a new class, **WIMS-LTI** will send a mail using the language found
in the LTI request. If there is no subdirectory for a given language, `en/` will
be used.
