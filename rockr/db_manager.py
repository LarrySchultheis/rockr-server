from rockr import db

# definitely room to clean this up in the future
# selecting records can take advantage of sqlalchemy
# queries like: User.query.get(username='Laer Bear')
# reference https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/


def insert(obj):
    db.session.add(obj)
    db.session.commit()


def delete(obj):
    db.session.delete(obj)
    db.session.commit()