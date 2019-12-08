import os

basedir = os.path.abspath(os.path.dirname(__name__))


class Config(object):
    FLASK_DEBUG = True
    SECRET_KEY = "secret-key"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
