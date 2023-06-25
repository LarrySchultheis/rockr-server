
class SerializerMixin:
    # all models should use this mixin, so we can serialize
    # and deserialize the objects
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def from_dict(self):
        pass