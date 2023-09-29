#!/usr/bin/env python3
from app.models.compound import CompoundProperty
from ..models.utils import _concat_properties
from .. import models as mdl
from marshmallow import post_dump
from app import db, ma

class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = mdl.Item
        additional = (
            "plate_name",
            "cell_name",
            "cell_code",
            "stack_name",
            "modality_name",
            "modality_target",
            "compound_concentration",
            "compound_name",
            "compound_property_id",
            "compound_moa_group",
            "compound_moa_subgroup",
            "compound_target",
            "timepoint_time",
            "timepoint_id",
            "section_id",
            "tags",
        )

    @post_dump()
    def concat_compound_props(self, data, **kwargs):
        data = _concat_properties(
            db,
            CompoundProperty,
            data,
            prefix="compound_",
            id_field="compound_property_id",
            **kwargs,
        )
        return data



class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = mdl.Tag
