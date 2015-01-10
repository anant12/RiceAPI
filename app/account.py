# ACCOUNT.PY
# Handles logic related to creating a new account or viewing details about an existing account.


import random

from flask import session, render_template, redirect

from app import app, db
from app.database import User
import config


alphanumeric = "abcdefghijklmnopqrstuvwxyz0123456789"


@app.route('/api_key')
def api_key():
    """
    Page for generating or displaying the user's API key.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = User.query.filter_by(net_id=net_id).first()
    if net_id is None:
        return redirect('/login')
    if user is None:
        # This person does not generated an API key yet
        return render_template('api_key.html', data={"net_id": net_id, "api_key": None})
    else:
        # This person has generated an API key
        return render_template('api_key.html', data={"net_id": net_id, "api_key": user.api_key})


@app.route('/generate_api_key')
def generate_api_key():
    """
    Generates a random API key associated with the logged in Net ID and adds that user to the database.
    """
    net_id = session.get(app.config['CAS_USERNAME_SESSION_KEY'], None)
    user = User.query.filter_by(net_id=net_id).first()
    if user is None:
        # Generate a string representation of a random, 30-character alphanumeric sequence
        api_key_list = [alphanumeric[random.randint(0, len(alphanumeric) - 1)] for i in range(config.API_KEY_LENGTH)]
        api_key = "".join(map(str, api_key_list))
        # Create the user and commit to the database
        user = User(net_id, api_key)
        db.session.add(user)
        db.session.commit()
    return redirect('/api_key')