import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Required for Flask sesion
SECRET_KEY = 'U\t\xeb\xec\xdf\xebS\xe7f\x10MFE\xd3\xaaQ\xbd\x8ehGU\x84\xf3\xcd'

# Length of generated alphanumeric API key
API_KEY_LENGTH = 30

# Location of SQLite database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'users.db')

# CAS authentication
CAS_SERVER = 'https://netid.rice.edu'
CAS_AFTER_LOGIN = 'after_login'