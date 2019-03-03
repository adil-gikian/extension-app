from flask_sqlalchemy import Model, SQLAlchemy
from sqlalchemy import Column, DateTime
from datetime import datetime

class TimestampedModel(Model):
    created_at = Column(DateTime, default=datetime.utcnow)

db = SQLAlchemy(model_class=TimestampedModel)


class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = (db.UniqueConstraint('handler'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    handler = db.Column(db.String())

    def __init__(self, name, handler):
        self.name = name
        self.handler = handler

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'handler': self.handler,
            'created_at': self.created_at
        }

class Edits(db.Model):
    __tablename__ = 'edits'

    id = db.Column(db.Integer, primary_key=True)
    handler = db.Column(db.String())
    finalTweet = db.Column(db.String())
    edits = db.Column(db.String())
    noOfEdits = db.Column(db.String())
    messageShown = db.Column(db.String())

    def __init__(self, handler, finalTweet, edits, noOfEdits,messageShown ):
        self.finalTweet = finalTweet
        self.edits = edits
        self.messageShown = messageShown
        self.noOfEdits = noOfEdits
        self.handler = handler

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'finalTweet': self.finalTweet,
            'edits': self.edits,
            'messageShown': self.messageShown,
            'noOfEdits': self.noOfEdits,
            'handler': self.handler,
            'created_at': self.created_at
        }
