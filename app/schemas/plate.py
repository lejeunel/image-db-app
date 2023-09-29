#!/usr/bin/env python3

from app import ma
from app.models.plate import Plate


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
