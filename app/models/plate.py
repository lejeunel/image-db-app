import uuid

from app import db
from sqlalchemy import func
from sqlalchemy_utils.types.uuid import UUIDType


class Plate(db.Model):
    __tablename__ = "plate"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    origin = db.Column(db.String(100))
    comment = db.Column(db.Text())
    project = db.Column(db.String(100))

    def __repr__(self):
        return f"<Plate {self.name} ({self.id})>"

