#!/usr/bin/env python3
from app import ma

from ..models.cell import Cell


class CellSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cell
