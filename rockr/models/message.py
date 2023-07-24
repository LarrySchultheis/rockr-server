from rockr import db
from .mixins import SerializerMixin
from .user import User


# a users contacts are all of their accepted matches
class UserMessageGroup(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)


class Message(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    message = db.Column(db.Text, nullable=False)
    ts = db.Column(db.DateTime, nullable=False)

    def __init__(self, message):
        self.sender_id = message['sender_id']
        self.recipient_id = message['recipient_id']
        self.message = message['message']
        self.ts = message['ts']