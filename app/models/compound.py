import enum
import uuid

from app import db, ma
from marshmallow import post_dump, pre_dump
from sqlalchemy import Enum
from sqlalchemy_mptt.mixins import BaseNestedSets
from sqlalchemy_utils.types.uuid import UUIDType

from .utils import _concat_properties


class CompoundPropertyType(enum.Enum):
    moa_group = "moa_group"
    moa_subgroup = "moa_subgroup"
    target = "target"


class CompoundProperty(db.Model, BaseNestedSets):
    __tablename__ = "compound_property"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(Enum(CompoundPropertyType))
    value = db.Column(db.String(100))

    def __repr__(self):
        return f"<CpdProperty {self.type}: {self.value}>"


class Compound(db.Model):
    __tablename__ = "compound"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    property_id = db.Column(db.ForeignKey("compound_property.id"))
    name = db.Column(db.String(100))
    bcs = db.Column(db.String(100))
    comment = db.Column(db.Text())

    def __repr__(self):
        return f"<Compound {self.name}>"



class CompoundSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Compound

    moa_group = ma.String(dump_only=True)
    moa_subgroup = ma.String(dump_only=True)
    target = ma.String(dump_only=True)
    property_id = ma.Int(required=False)

    @post_dump()
    def concat_compound_props(self, data, **kwargs):
        data = _concat_properties(
            db, CompoundProperty, data, prefix="", id_field="property_id", **kwargs
        )
        return data


class CompoundPropertySchema(ma.SQLAlchemySchema):
    class Meta:
        model = CompoundProperty
    id = ma.auto_field()
    type = ma.Enum(CompoundPropertyType)
    value = ma.auto_field()

