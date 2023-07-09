from rockr import db

# definitely room to clean this up in the future
# selecting records can take advantage of sqlalchemy
# queries like: User.query.get(username='Laer Bear')
# reference https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/


def select(obj):
    db.session.select(obj)


def select_all():
    db.session.select()


def insert(obj):
    db.session.add(obj)
    db.session.commit()


def delete(obj):
    db.session.delete(obj)
    db.session.commit()


# def update_from_json(obj, updates):
#     for k, v in updates.items():
#         setattr(obj, k, v) if v else None
#     db.session.commit()
#     db.session.refresh(obj)
#     return obj
