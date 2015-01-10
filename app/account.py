# ACCOUNT.PY
# Handles logic related to creating a new account or viewing details about an existing account.


import random
from flask import session
from app import app, db
from app.database import User
from werkzeug.utils import redirect
import config


alphanumeric = "abcdefghijklmnopqrstuvwxyz0123456789"


@app.route('/after_login')
def after_login():
    """
    Check if the logged in Net ID exists in the database. If it does, show the user his/her API key. If not, make one.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = User.query.filter_by(net_id=net_id).first()
    if user is None:
        # This person does not generated an API key yet
        return redirect('/generate_api_key')
    else:
        # This person has generated an API key
        return redirect('/')


@app.route('/generate_api_key')
def generate_api_key():
    """
    Generates a random API key associated with the logged in Net ID and adds that user to the database.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    # Generate a string representation of a random, 30-character alphanumeric sequence
    api_key_list = [alphanumeric[random.randint(0, len(alphanumeric) - 1)] for i in range(config.API_KEY_LENGTH)]
    api_key = "".join(map(str, api_key_list))
    # Create the user and commit to the database
    user = User(net_id, api_key)
    db.session.add(user)
    db.session.commit()
    return "Success!"