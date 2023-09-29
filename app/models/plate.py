import uuid

from app import db, ma
from marshmallow import post_dump
from sqlalchemy import func
from sqlalchemy_utils.types.uuid import UUIDType

from .timepoint import TimePoint, TimePointSchema


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

class PlateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Plate

    # timepoints = ma.List(ma.Nested(TimePointSchema))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("Plate.PlateAPI", values=dict(id="<id>")),
            "collection": ma.URLFor("Plate.PlatesAPI"),
            "timepoints": ma.URLFor('Plate.get_timepoints', values={'id': '<id>'}),
            "sections": ma.URLFor('Section.SectionsAPI', values={'id': '<id>'}),
        }
    )
