#!/usr/bin/env python3

from app.extensions import ma
from app.models.plate import Plate


class PlateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Plate

    # timepoints = ma.List(ma.Nested(TimePointSchema))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("Api.Plate.Plate", values=dict(id="<id>")),
            "collection": ma.URLFor("Api.Plate.Plates"),
            "timepoints": ma.URLFor('Api.Plate.get_timepoints', values={'id': '<id>'}),
            "sections": ma.URLFor('Api.Section.Sections', values={'id': '<id>'}),
        }
    )
