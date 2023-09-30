import uuid

from app.extensions import db, ma
from sqlalchemy import func
from sqlalchemy_utils.types.uuid import UUIDType


class TimePoint(db.Model):
    __tablename__ = "timepoint"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    uri = db.Column(db.String(300))
    plate_id = db.Column(db.ForeignKey("plate.id"))

    def __repr__(self):
        return f"<TimePoint {self.uri} ({self.id})>"


