import os


class Config(object):
    """
    Base class to change Config Details for the application
    """
    """
    Flask Main Configurations
    """
    port = 8069
    DEBUG = True
    SECRET_KEY = "streaming_platform_debug_code"
    threaded = True
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    APP_STATIC = os.path.join(APP_ROOT, 'static')
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads/')

    # Database name used by PyMongo
    MONGO_DBNAME = 'stream'


class ProductionConfig(Config):
    """
    These settings apply to the application if the applications is
    in the production Phase
    """
    DEBUG = True


class DevelopmentConfig(Config):
    """
    These settings apply to the application if the applications is
    in the Development Phase.If you are a developer you should choose these
    settings
    """
    DEBUG = True


config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)
