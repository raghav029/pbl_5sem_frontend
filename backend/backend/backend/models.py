from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from uuid import uuid4
import datetime

db = SQLAlchemy()
ma = Marshmallow()

def get_uuid():
    return uuid4().hex
# parent class or Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    usn = db.Column(db.String(32))
    username = db.Column(db.String(32))
    email = db.Column(db.String(354), unique=True)
    password = db.Column(db.Text, nullable=False)
    ph_number = db.Column(db.Integer()) 
    user_events = db.relationship('UserEvent', backref = 'users', lazy=True)

    def __init__(self, usn, email, password, ph_number, username):
        self.usn = usn
        self.email = email
        self.password = password
        self.ph_number = ph_number
        self.username = username

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'ph_number', 'username')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


# Parent class or Model
class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(40))
    title = db.Column(db.String(50))
    description = db.Column(db.Text())
    dept = db.Column(db.String(20))
    date = db.Column(db.DateTime, default=datetime.datetime.now) 
    user_events = db.relationship('User', secondary='user_event', backref = 'events', lazy=True)

    def __init__(self, image, title, description, dept):
        self.image = image
        self.title = title
        self.description = description
        self.dept = dept

class EventSchema(ma.Schema):
    class Meta:
        fields = ('id', 'image', 'title', 'description', 'dept', 'date')

event_schema = EventSchema()
events_schema = EventSchema(many=True)


# Child class (many-to-many model which is refrencing to two tables User and Events)
class UserEvent(db.Model):
    __tablename__ = 'user_event'
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    applied = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, event_id, applied):
        self.user_id = user_id
        self.event_id = event_id
        self.applied = applied  

class UserEventSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'event_id', 'applied')

UserEvent_schema = UserEventSchema()
UserEvents_schema = UserEventSchema(many=True)

