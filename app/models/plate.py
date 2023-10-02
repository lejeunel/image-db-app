import uuid

from app.extensions import db
from sqlalchemy import func
from sqlalchemy_utils.types.uuid import UUIDType
from .mixins import UpdateMixin


class Plate(db.Model, UpdateMixin):
    __tablename__ = "plate"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    origin = db.Column(db.String(100))
    comment = db.Column(db.Text())
    project = db.Column(db.String(100))
    stack_id = db.Column(UUIDType, db.ForeignKey("stack.id"))

    def __repr__(self):
        return f"<Plate {self.name} ({self.id})>"

