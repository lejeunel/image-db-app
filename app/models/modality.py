import uuid

from app.extensions import db
from sqlalchemy_utils.types.uuid import UUIDType
from .mixins import UpdateMixin

class Modality(db.Model, UpdateMixin):
    __tablename__ = "modality"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(100))
    target = db.Column(db.String(100))
    comment = db.Column(db.Text())

    def __repr__(self):
        return f"<Modality {self.name}>"

