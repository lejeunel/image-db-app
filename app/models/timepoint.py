import uuid

from app import db, ma
from sqlalchemy import func
from sqlalchemy_utils.types.uuid import UUIDType
from flask import current_app
from marshmallow import validate
from urllib.parse import urlparse


class TimePoint(db.Model):
    __tablename__ = "timepoint"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    uri = db.Column(db.String(300))
    plate_id = db.Column(db.ForeignKey("plate.id"))

    def __repr__(self):
        return f"<TimePoint {self.uri} ({self.id})>"


class TimePointSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TimePoint

    ok_schemes = current_app.config["PARSER_SUPPORTED_SCHEMES"]
    uri = ma.String(
        validate=[validate.URL(
            schemes=ok_schemes,
            require_tld=False,
            error="{input} is not a valid URI. " + "Allowed schemes are {}".format(
                ok_schemes
            ),
        ), validate.Regexp(regex='^.*\/$', error="{input} is not a valid URI. It must end with /")]
    )
