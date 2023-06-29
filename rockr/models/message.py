from rockr import db
from .mixins import SerializerMixin


# a users contacts are all of their accepted matches
class UserMessageGroup(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('public.user.id'), nullable=False)


class Message(SerializerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message_group_id = db.Column(db.Integer, db.ForeignKey('public.usermesssagegroup.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('public.user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
