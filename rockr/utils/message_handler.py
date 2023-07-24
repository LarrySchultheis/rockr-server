from rockr import app, db, db_manager
from rockr.models import Message, User
from datetime import datetime

def save_message(req):
    print(req['sender']['email'])
    print(datetime.now().timestamp())
    sender_id = User.query.filter_by(email=req['sender']['email']).first().id
    recipient_id = req['recipient']['id']
    message_body = req['text']
    db.session.add(Message({"sender_id": sender_id, "recipient_id": recipient_id, "message": message_body, "ts": datetime.now()}))
    db.session.commit()
