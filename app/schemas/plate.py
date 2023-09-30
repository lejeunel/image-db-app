#!/usr/bin/env python3

from app.extensions import ma
from app.models.plate import Plate


class PlateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Plate

    # timepoints = ma.List(ma.Nested(TimePointSchema))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("Plate.Plate", values=dict(id="<id>")),
            "collection": ma.URLFor("Plate.Plates"),
            "timepoints": ma.URLFor('Plate.TimePointsOfPlate', values={'id': '<id>'}),
            "sections": ma.URLFor('Plate.SectionsOfPlate', values={'id': '<id>'}),
            "stack": ma.URLFor("Plate.get_stack", values={'id': '<id>'})
        }
    )
