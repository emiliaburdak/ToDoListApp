from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

note_hashtags = db.Table('note_hashtags',
                         db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True),
                         db.Column('hashtag_id', db.Integer, db.ForeignKey('hashtag.id'), primary_key=True),
                         )


class Hashtag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean)
    important = db.Column(db.Boolean)
    category = db.Column(db.String(100))
    hashtags = db.relationship('Hashtag', secondary=note_hashtags, backref=db.backref('Notes', lazy='dynamic'))
    day = db.Column(db.String(100))
    raw_text = db.Column(db.String(10000))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    hashtags = db.relationship('Hashtag')
