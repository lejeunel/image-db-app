#!/usr/bin/env python3
from app import db, ma
from marshmallow import post_dump, validates_schema, ValidationError
from app.models.compound import CompoundPropertyType

from ..models.utils import _concat_properties
from .. import models as mdl


class CompoundSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = mdl.Compound

    moa_group = ma.String(dump_only=True)
    moa_subgroup = ma.String(dump_only=True)
    target = ma.String(dump_only=True)
    property_id = ma.Int(required=False)

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("Compound.Compounds", values=dict(id="<id>")),
            "collection": ma.URLFor("Compound.Compounds"),
            "properties": ma.URLFor("CompoundProperty.CompoundProperty", values=dict(id="<property_id>")),
        }
    )

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
    parent_id = ma.auto_field()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("CompoundProperty.CompoundProperty", values=dict(id="<id>")),
            "collection": ma.URLFor("CompoundProperty.CompoundProperties"),
        }
    )

    @validates_schema
    def validate_root_node_type(self, data, **kwargs):
        """
        Checks that a parent_id must be given when type is different
        than "root" type (level 0)
        """

        root_type = CompoundPropertyType(0)
        if (data['type'] != root_type) and ('parent_id' not in data):
            raise ValidationError(f"For type different than {root_type.name}, provide parent_id!")
