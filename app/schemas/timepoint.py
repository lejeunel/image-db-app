#!/usr/bin/env python3
from app.extensions import ma
from app import models as mdl
from flask import current_app
from marshmallow import validate

class TimePointSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = mdl.TimePoint

    plate_id = ma.UUID()
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

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("TimePoint.TimePoint", values=dict(id="<id>")),
            "collection": ma.URLFor("TimePoint.TimePoints"),
            'plate': ma.URLFor("Plate.Plate", values=dict(id="<plate_id>"))
        }
    )
