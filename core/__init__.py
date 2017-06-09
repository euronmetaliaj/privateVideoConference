from .configurations import config_by_name
from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
import logging
from logging.handlers import RotatingFileHandler


# Authentication : Login,Logout, Register
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'authentication.login'

# Logging : Infos ,Alerts and Other Logs
handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)


# Mongo Database definition
database = PyMongo()


def create_app(config_name):
    """
    Create the flask application
    :param config_name:dev for development ,prod for production
    :return:flask application
    """
    app = Flask(__name__)
    app.config.from_object(configurations.config_by_name[config_name])

    login_manager.init_app(app)
    database.init_app(app)
    app.logger.addHandler(handler)

    # Declaration of the blueprints
    # Authentication : Login, Logout, Register
    from .authentication import authentication
    app.register_blueprint(authentication)

    # User Managment : Delete , Add
    from .users import users
    app.register_blueprint(users)

    return app
