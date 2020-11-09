# Django-user-register-email-edit
# Depot 
> 
 * Une page Web permettant à un utilisateur de se connecter.
 *  Une fois connecté, l'utilisateur accède à une page pour afficher / modifier ses informations.
 * En cliquant sur "Modifier ses informations", on veut avoir une modale qui s'ouvre.
 *  Dans cette modale,  on veut un input permettant de modifier son adresse email, ainsi qu'un bouton "enregistrer". A l'appui de ce bouton, l'adresse email sera modifiée dans la base de données et sur la page principale sans rechargement de la page.
 * Le code python doit être écrit en Orienté Objet.
>

## Technos :  
* Django, Python3, Sqlite3 Bootstrap et jQuery et Docker.
## Utilisation : 

```bash
$ git clone https://github.com/bakidjan/Django-user-register-email-edit.git
```
## Démarrer le serveur sur Docker : 

```bash
$ docker-compose up
```
## Démarrer le serveur sur Django : 

```bash
$ python3 mange.py runserver
```
# ensuite aller sur un navigateur web pour lancer l'application
```bash
$ http://0.0.0.0:8000/
```
url d'accès à l'accueil
```bash
$ http://0.0.0.0:8000/index/
```
url d'accès à la modification de l'adresse email
```bash
$ http://0.0.0.0:8000/authentified/
```
