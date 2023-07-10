from flask import jsonify


class SerializerMixin:
    # all models should use this mixin, so we can serialize
    # and deserialize the objects
    def serialize(self):
        as_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return as_dict

    def deserialize(self):
        pass

    # doesn't go here semantically, but use for PATCH requests
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
