#!/usr/bin/env python3
from app import ma

from ..models.cell import Cell


class CellSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cell

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("Cell.Cell", values=dict(id="<id>")),
            "collection": ma.URLFor("Cell.Cells"),
        }
    )
