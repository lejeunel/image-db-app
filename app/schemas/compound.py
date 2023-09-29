#!/usr/bin/env python3
from app import db, ma
from marshmallow import post_dump

from ..models.utils import _concat_properties
from .. import models as mdl


class CompoundSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = mdl.Compound

    moa_group = ma.String(dump_only=True)
    moa_subgroup = ma.String(dump_only=True)
    target = ma.String(dump_only=True)
    property_id = ma.Int(required=False)

    @post_dump()
    def concat_compound_props(self, data, **kwargs):
        data = _concat_properties(
            db, mdl.CompoundProperty, data, prefix="", id_field="property_id", **kwargs
        )
        return data


class CompoundPropertySchema(ma.SQLAlchemySchema):
    class Meta:
        model = mdl.CompoundProperty
    id = ma.auto_field()
    type = ma.Enum(mdl.CompoundPropertyType)
    value = ma.auto_field()
