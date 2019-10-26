from manage import db,app
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80),nullable=False)
    events = db.relationship('Events', backref='author', lazy=True)
    def __repr__(self):
        return 'User {} and Id {}'.format(self.username,self.id)

class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_type = db.Column(db.String(20),nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    location = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '{} {} {} {} {} {}'.format(self.id,self.title,self.date_posted,
        self.content,self.event_type,self.location)

class Attendees(db.Model):
    __tablename__ = 'attendees'
    id = db.Column(db.Integer, primary_key=True)
    mailid = db.Column(db.String(120),nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    def __repr__(self):
        return f'{self.id} {self.user_id} {self.event_id}'

class PrivateJoinReq(db.Model):
    __tablename__ = 'private_join_req'
    id = db.Column(db.Integer, primary_key=True)
    mailid = db.Column(db.String(120),nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    def __repr__(self):
        return f'{self.id} {self.mailid} {self.event_id}'
