import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Required for Flask session
SECRET_KEY = str(os.urandom(24))

# Length of generated alphanumeric API key
API_KEY_LENGTH = 30

# Location of SQLite database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'users.db')

# CAS authentication
CAS_SERVER = 'https://netid.rice.edu'
CAS_AFTER_LOGIN = 'api_key'