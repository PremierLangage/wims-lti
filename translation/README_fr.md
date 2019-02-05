
# WIMS-LTI

**WIMS-LTI** est un serveur servant de passerelle entre un *LMS* et un serveur
*WIMS* grâce à la norme *LTI*.



## Introduction

**WIMS-LTI** permet :

* De créer une classe *WIMS* associée a un cours d'un *LMS*
* De créer les élèves correspondant à ce cours dans la classe *WIMS*
* Aux élèves de ce cours de se connecter au serveur *WIMS* depuis le *LMS*
* Aux professeurs de se connecter à la classe *WIMS* en tant que superviseur
  ou en tant qu'élève.



## Comment ça marche ?

Une fois la passerelle **WIMS-LTI** installée, il est possible d'ajouter des
*LMS* ainsi que des serveurs *WIMS* depuis le panneau d'administration de
celle-ci.

Chaque serveur *WIMS* est associé à une URL LTI, qui peut être utilisée depuis
n'importe quel *LMS* ajouté à **WIMS-LTI** afin de se connecter au serveur
*WIMS* depuis celui-ci.

Lorsqu'un utilisateur du LMS clique sur un lien LTI depuis celui-ci,
voici ce qu'il se passe :

1. Si la classe associée à ce cours n'existe pas sur le serveur WIMS :
    * Si l'utilisateur est professeur (ou autres rôles autorisés), la classe
      est créée et l'utilisateur est connecté en tant que superviseur.
    * Sinon, une réponse `403 Accès refusé` est envoyée à l'utilisateur.

2. Si la classe existe :
    * Si l'utilisateur est professeur (ou autres rôles autorisés), il est
      connecté en tant que superviseur.
    * Sinon, si l'élève associé à cette utilisateur existe dans la classe
      *WIMS*, celui-ci est connecté en tant qu'étudiant.
    * Enfin, si l'élève associé à cette utilisateur n'existe pas dans la classe
      *WIMS*, il est créé avec pour nom pseudo
      `[première lettre du prénom] + [nom]`, un entier étant ajouté à la fin si
      ce pseudo est déjà pris. Une fois l'élève créer sur la classe WIMS,
      celui-ci est connecté au serveur WIMS en tant qu'étudiant.



## Installation


#### Dépendances

* Python 3.5+
* pip3
* Apache2 & mod_wsgi

<br>

Dans un premier temps, clonez le dépot :

```bash
git clone https://openproject.u-pem.fr/git/wims-lti.git
cd wims-lti
```

Puis, modifier le fichier `wimsLTI/config.py` pour modifier certain paramètres par 
défaut, voir  [la référence des paramètres](https://docs.djangoproject.com/fr/2.1/ref/settings/).
Dans un premier temps, il est important de décommenter la ligne `DEBUG = False` et de modifier
les paramètres 
[`SECRET_KEY`](https://docs.djangoproject.com/fr/2.1/ref/settings/#std:setting-SECRET_KEY) et
[`ALLOWED_HOSTS`](https://docs.djangoproject.com/fr/2.1/ref/settings/#allowed-hosts).

Une fois les paramètres correctement définis, lancez ensuite le script d'installation,
celui-ci vous demandera un nom d'utilisateur, une adresse email ainsi qu'un mot de passe
afin de créer un compte administrateur.


***Attention : Si vous utilisez un
[environment python](https://docs.python.org/fr/3/tutorial/venv.html),
n'oubliez pas de le lancer.***

```bash
./install.sh
```

Il ne reste maintenant plus qu'à configurer *Apache*, voir
[la documentation](https://docs.djangoproject.com/fr/2.1/howto/deployment/wsgi/modwsgi/).


## Configuration

### Coté WIMS

Afin que le serveur *WIMS* accepte les requêtes de **WIMS-LTI**, il est
nécessaire d'y créer un fichier de connexion. La définition de ce fichier est
expliqué [ici](https://wimsapi.readthedocs.io/#configuration).

Il est important d'ajouter l'IP de la **passerelle** à la clé `ident_site`, et nom
l'IP du *LMS*.

Retenez bien la valeur de la clé `ident_password` ainsi que le nom du fichier
créé. Ces informations seront nécessaires pour ajouter le serveur à
**WIMS-LTI**.


### Coté WIMS-LTI


1. Se connecter a `[WIMS-LTI SERVEUR]/admin/` et rentrez les identifiants
   *admin* indiqués lors de l'installation du serveur.

2. Cliquez sur `wims` (ou aller à `[WIMS-LTI SERVEUR]/admin/wims/wims/`).

3. Cliquer sur `ADD WIMS` en haut à gauche, remplissez le formulaire :
    * `DNS` : DNS du serveur *WIMS*, ex: `wims.unice.fr`.
    * `URL` : URL du serveur *WIMS* CGI, ex: `https://wims.unice.fr/wims/wims.cgi`.
    * `Name` : Nom permettant de reconnaitre le serveur *WIMS*, ex: `WIMS UNICE`.
    * `Ident` : Nom du fichier de connexion créer sur le serveur *WIMS*, par
                exemple, si le fichier créé est `[WIMS_HOME]/log/classes/.connections/myself`,
                rentrez `myself`.
    * `Passwd` : Valeur de la clé `ident_password` du fichier de configuration *ident*.
    * `Rclass` : Identifiant utilisez par *WIMS-LTI* pour créer les classes sur
                 le serveur *WIMS*, ex: `myclass`.
    
    Répéter ***3.*** pour chaque serveur *WIMS* que vous souhaitez ajouter.

4. Retourner sur `[WIMS-LTI SERVEUR]/admin/` et cliquer sur `LMS` (ou aller à 
   `[WIMS-LTI SERVEUR]/admin/wims/lms/`)

5. Cliquer sur `ADD LMS` en haut à gauche et remplissez le formulaire :
    * `UUID` : UUID du *LMS* correspondant au paramètre `tool_consumer_instance_guid`
               de la requête LTI. Il s'agit le plus souvent du DNS du *LMS*,
               ex: `elearning.u-pem.fr`
    * `Name` : Nom permettant de reconnaitre le *LMS*, ex: `Moodle UPEM`.
    * `URL` : URL du *LMS*, ex: `https://elearning.u-pem.fr/`
    
    Répéter ***5.*** pour chaque *LMS* que vous souhaitez ajouter.


___


Il est maintenant possible de se connecter à n'importe quel serveur *WIMS*
ajouté, depuis n'importe quel *LMS* ajouté grâce aux URLs:

* `[WIMS-LTI SERVEUR]/dns/[WIMS DNS]/` -
  par exemple : `https://wims-lti.u-pem.fr/dns/wims.u-pem.fr/`

ou

* `[WIMS-LTI SERVEUR]/dns/[WIMS ID]/` - où `WIMS ID` est l'ID du serveur *WIMS*
  dans la base de données de **WIMS-LTI**,
  par exemple : `https://wims-lti.u-pem.fr/id/0/`


La liste des URLs peut être trouvée sur la page `[WIMS-LTI SERVEUR]/list/`
