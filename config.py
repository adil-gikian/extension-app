import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    #SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = 'postgres://xghjfozhdmbkdo:78c4a3adb92ea8f1b8d135888040a87320903e6c83ea786007839cef97ffd164@ec2-54-247-82-210.eu-west-1.compute.amazonaws.com:5432/d8h6ie6g74jmgo'


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True