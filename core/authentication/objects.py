from flask_wtf import Form
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import (DataRequired, Length, Regexp, EqualTo, Email, ValidationError, URL)
from flask_login import UserMixin
from core import database
from manage import app
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import random


class LoginForm(Form):
    """
    Class for the form of the login defined in login.html
    It has the authentication attributes of the form in login.html
    """
    username = StringField("Your Username:", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


# User Class
class User(UserMixin):
    """
    Collection : Users

    """

    def __init__(self, name=None, email=None, username=None, pw_hash=None, password=None, id=None, ip_address=None,
                 phone=None, city=None, administrator=False, active=False):
        self.username = username
        self.active = active
        self.email = email
        self.name = name
        self.city = city
        self.id = id
        self.administrator = administrator
        self.phone = phone
        self.ip_address = ip_address
        if not password or pw_hash:
            import string
            password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(0, 6))
        self.pw_hash = pw_hash or self.set_password(password)
        self.password = password

    @staticmethod
    def set_password(password):
        return generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.pw_hash, password)

    def save(self):
        if not self.id:

            # Check if user exists in database
            if not database.db.Users.find_one({
                'username': self.username,
                'pw_hash': self.pw_hash
            }):

                # If username was not provided , safely create a new one ,If it exists create a new one
                if not self.username:
                    while True:
                        self.username = self.name.lower().replace(' ', '') + str(random.randint(0, 10))
                        if not User.load_user_from_username(username=self.username):
                            break

                # Add user to database
                database.db.Users.insert({
                    'username': self.username,
                    'pw_hash': self.pw_hash,
                    'name': self.name,
                    'phone': self.phone,
                    'email': self.email,
                    'city': self.city,
                    'active': self.active,
                    'administrator': self.administrator,
                    'ip_address': self.ip_address
                })
                app.logger.info('A user with username ' + str(self.username) + ' has been created!')
                return True
            else:
                app.logger.info('A user with username ' + str(self.username) + ' exists!Cannot create new one!')
                return False

    def toogle_activation(self):
        self.active = False if self.active else True
        print self.active
        if database.db.Users.find_and_modify(query={'_id': self.id}, update={"$set": {
            "active": self.active
        }}):
            return True
        else:
            self.active = False if self.active else True
            return False

    def deleteUser(self):
        return database.db.Users.delete_one({'_id': self.id})

    @classmethod
    def load_user_from_username(cls, username):
        user = database.db.Users.find_one({'username': username})
        if user:
            return cls(username=user['username'], id=user['_id'], pw_hash=user['pw_hash'], email=user['email'],
                       name=user['name'], ip_address=user['ip_address'], phone=user['phone'], city=user['city'],
                       administrator=user['administrator'], active=user['active'])

    @classmethod
    def load_user_from_id(cls, id):
        user = database.db.Users.find_one({'_id': ObjectId(id)})
        if user:
            return cls(username=user['username'], id=user['_id'], pw_hash=user['pw_hash'], email=user['email'],
                       name=user['name'], ip_address=user['ip_address'], phone=user['phone'], city=user['city'],
                       administrator=user['administrator'], active=user['active'])

    @staticmethod
    def load_user(username, password):
        user = User.load_user_from_username(username)
        return user if user and user.check_password_hash(password) else None


    @staticmethod
    def get_all_users():
        res = []
        users_ids = database.db.Users.find({})
        for user in users_ids:
            res.append(User.load_user_from_id(user['_id']))
        return res
