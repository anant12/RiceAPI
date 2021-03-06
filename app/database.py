# DATABASE.PY
# Handles logic related to account storage in the database.


from app import db


class User(db.Model):
    """
    Model representing an authorized user. Consists of a Net ID and an auto-generated API key
    """
    net_id = db.Column(db.String(10), primary_key=True, unique=True)
    api_key = db.Column(db.String(120))

    def __init__(self, net_id, api_key):
        self.net_id = net_id
        self.api_key = api_key

    def __repr__(self):
        return '<User %r>' % self.net_id


class Reservation(db.Model):
    """
    Model representing cached Fondren reservation information.
    Used for faster API response
    """
    room_number = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    description = db.Column(db.String(120))
    availability = db.Column(db.String)

    def __init__(self, room_number, description, availability):
        self.room_number = room_number
        self.description = description
        self.availability = availability

    def __repr__(self):
        return '<Reservation %r>' % self.room_number