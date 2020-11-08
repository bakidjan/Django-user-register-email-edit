import re
import random
import sqlite3

from hashlib import sha256

from django.http import JsonResponse, HttpResponse, HttpResponseRedirect

from . import settings


def valid_email(email) -> bool:
    # vu la gueule du truc, j'ai bien fait de la copier de :
    # https://stackoverflow.com/a/43937713
    return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email))

def create_password() -> str:
    # p'tit truc naif pour créer des mots de passes aléatoires mais prononcables
    # c'est un bricol farfelux mais il marche bien
    voyelles = "aeiou"
    consonnes = "".join([chr(i) for i in range(97, 97 + 26) if not chr(i) in voyelles])
    voyelles, consonnes = list(voyelles), list(consonnes)
    random.shuffle(voyelles)
    random.shuffle(consonnes)
    password = ''.join([voyelles[i] + consonnes[i] for i in range(3)]) + str(random.randint(100, 999))
    return password

class UserDoesNtExistExceptionWithLongName(Exception):
    pass

def catch_user_exception(func):
    """Decorator to handle the 
    `UserDoesNtExistExceptionWithLongName` exception.

    Return a JSON responde with the error code 400.

    (ça m'évite surtout de faire des gros try catch degueulasses)
    """
    #honteusement pompé sur : 
    #https://medium.com/swlh/handling-exceptions-in-python-a-cleaner-way-using-decorators-fae22aa0abec
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UserDoesNtExistExceptionWithLongName:
            return JsonResponse({
                'status_code': 400,
                'error': 'Hummm... how to say that in a polite way ??!! "Flute ! cet utilisateur ne nous est pas familier cher monsieur..."'
            })
    return inner_function

class Users:
    # Create the database with the example user if not already exists
    # in a static way to be sure it's runned at the server start
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            mail    STRING NOT NULL,
            pwd     STRING NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    @staticmethod
    def user_exists(mail_or_id) -> bool:
        """Check if the user exists.

        :param mail_or_id: 
            if this variable is an int, it's assumed 
            it's the user id else the user email

        :return: if the user exists in the database (quite obvious, don't you think ??!!)
        """
        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()

        if type(mail_or_id) is int:
            c.execute("""
                SELECT 1 FROM Users
                WHERE id=?
            """, (mail_or_id,))
        else: #mail
            c.execute("""
                SELECT 1 FROM Users
                WHERE mail=?
            """, (mail_or_id,))
        
        conn.commit()
        
        exists = bool(len(list(c)))
        
        conn.close()

        return exists
    
    @staticmethod
    def get_user_id(mail: str) -> int:
        if not Users.user_exists(mail):
            raise UserDoesNtExistExceptionWithLongName(f"User {mail} do not exists...")

        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute("""
            SELECT id FROM Users
            WHERE mail=?
            LIMIT 1
        """, (mail,))
        conn.commit()
        
        [(user_id,)] = list(c)
        
        conn.close()

        return user_id

    @staticmethod
    def get_user_email(user_id: int) -> str:
        if not Users.user_exists(user_id):
            raise UserDoesNtExistExceptionWithLongName(f"User {user_id} do not exists...")

        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute("""
            SELECT mail FROM Users
            WHERE id=?
            LIMIT 1
        """, (user_id,))
        conn.commit()
        
        [(mail,)] = list(c)
        
        conn.close()

        return mail

    @staticmethod
    def add_user(mail: str, pwd: str = "password") -> bool:
        if Users.user_exists(mail):
            return False # Can't create the user, creation failed
        
        pwd = sha256(pwd.encode()).hexdigest()

        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute("""
            INSERT INTO Users (mail, pwd)
            VALUES (?, ?)
        """, (mail, pwd))
        conn.commit()
        conn.close()

        return bool(Users.user_exists(mail))

    @staticmethod
    def get_password_hash(mail: str) -> str:
        if not Users.user_exists(mail):
            raise UserDoesNtExistExceptionWithLongName(f"User {mail} do not exists...")

        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute("""
            SELECT pwd FROM Users
            WHERE mail=?
            LIMIT 1
        """, (mail,))
        conn.commit()
        
        [(pwd,)] = list(c)
        
        conn.close()

        return pwd

    @staticmethod
    def change_email(mail: str, new_mail: str) -> bool:
        if not Users.user_exists(mail):
            return False
        
        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute("""
            UPDATE Users
            SET mail=?
            WHERE mail=?;
        """, (new_mail, mail))
        conn.commit()
        conn.close()

        return bool(Users.user_exists(new_mail))


class Server:
    @staticmethod
    @catch_user_exception
    def create_user(request):
        if "mail" in request.GET:
            mail = request.GET["mail"]
        elif "mail" in request.POST:
            mail = request.POST["mail"]
        else:
            return  JsonResponse({
                'status_code': 400,
                'error': 'The field `mail` should be specified...'
            })
        if not valid_email(mail):
            return JsonResponse({
                'status_code': 400,
                'error': 'The `mail` field is poorly formated...'
            })
        
        created_random_password = False
        if "pwd" in request.GET: #should not be there... but if user is dumb... let it goooooooo...
            pwd = request.GET["pwd"]
        elif "pwd" in request.POST and request.POST['pwd'] != '':
            pwd = request.POST["pwd"]
        else: # Affect a default password
            pwd = create_password()
            created_random_password = True
        
        user_creation_success = Users.add_user(mail, pwd)

        if not user_creation_success and Users.user_exists(mail):
            return JsonResponse({
                'status_code': 400,
                'error': 'The mail provided already exists...'
            })
        elif not user_creation_success:
            return JsonResponse({
                'status_code': 500,
                'error': 'Failed to create you an account...'
            })
        
        request.session['user_id'] = Users.get_user_id(mail)

        if created_random_password:
            return JsonResponse({
                'status_code': 200,
                'text': f'Your default password is : {pwd}'
            })
        else:
            return JsonResponse({
                'status_code': 200,
                'text': 'Account successfully created !'
            })

    @staticmethod
    @catch_user_exception
    def loggin(request):
        if "user_id" in request.session:
            return JsonResponse({
                'status_code': 200,
                'text': 'Already logged...'
            })

        if not ("mail" in request.POST and "pwd" in request.POST):
            return JsonResponse({
                'status_code': 400,
                'error': "`mail` and `pwd` should be provided via a POST call..."
            })
        
        mail = request.POST['mail'].strip()
        pwd  = request.POST['pwd']

        if not Users.user_exists(mail):
            return JsonResponse({
                'status_code': 400,
                'error': 'This email adress do not exist FDP !'
            })
        
        # Check if the passwords match
        if sha256(pwd.encode()).hexdigest() != Users.get_password_hash(mail):
            return JsonResponse({
                'status_code': 400,
                'error': 'Password do not match...'
            })


        user_id = Users.get_user_id(mail)
        request.session['user_id'] = user_id

        return JsonResponse({
            'status_code': 200,
            'text': "You're logged now..."
        })

    @staticmethod
    @catch_user_exception
    def change_email(request):
        if not 'user_id' in request.session:
            return JsonResponse({
                'status_code': 403,
                'error': 'You need to be logged to use this function...'
            })
        

        mail = Users.get_user_email(int(request.session['user_id']))
        
        if "new_mail" in request.GET:
            new_mail = request.GET["new_mail"]
        elif "new_mail" in request.POST:
            new_mail = request.POST["new_mail"]
        else:
            return  JsonResponse({
                'status_code': 400,
                'error': 'The field `new_mail` should be specified...'
            })

        if mail == new_mail:
            return JsonResponse({
                'status_code': 400,
                'error': "C'est déjà ton email gros con !"
            })

        if Users.user_exists(new_mail):
            return JsonResponse({
                'status_code': 403,
                'error': 'This email is already used by somebody else...'
            })

        return JsonResponse({
            'status_code': 200,
            'text': 'Your email has been updated...'
        }) if Users.change_email(mail, new_mail) else JsonResponse({
            'status_code': 500,
            'error': "We didn't manage to update your email with the information YOU provided..."
        })
    
    @staticmethod
    def loggout(request):
        if 'user_id' in request.session:
            del request.session['user_id']
            return JsonResponse({
                'status_code': 200,
                'text': 'Logged out...'
            })
        else:
            return JsonResponse({
                'status_code': 200,
                'text': "You'ren't logged abrutit !"
            })
        
class HTMLPages:
    @staticmethod
    def index(request):
        if 'user_id' in request.session:
            return HttpResponseRedirect("../authentified/")
        
        with open(f'{settings.STATIC_URL}/index.html', 'r') as f:
            return HttpResponse(f.read())
    
    @staticmethod
    def authentified(request):
        if not 'user_id' in request.session:
            return HttpResponseRedirect('../index/')
        
        with open(f'{settings.STATIC_URL}/authentified.html', 'r') as f:
            page = f.read()

            # en vrai ya moyen de gérer ça avec des templates et tout et tout
            user_id = request.session['user_id']
            mail = Users.get_user_email(user_id)
            pwd  = Users.get_password_hash(mail)
            for variable, value in [
                ('[[USER_EMAIL]]', mail),
                ('[[USER_PWD]]', pwd),
                ('[[USER_ID]]', str(user_id)),
                ('[[CURRENT_SESSION]]', request.session.session_key)
            ]:
                page = page.replace(variable, value)

            return HttpResponse(page)