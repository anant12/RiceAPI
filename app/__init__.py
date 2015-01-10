from flask import Flask
import flask.ext.sqlalchemy
from flask_cas import CAS


app = Flask(__name__)
app.config.from_object('config')
db = flask.ext.sqlalchemy.SQLAlchemy(app)
CAS(app)

app.config.setdefault('CAS_USERNAME_SESSION_KEY', 'CAS_USERNAME')

from app import api, account, database
