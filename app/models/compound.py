import enum
import uuid

from app.extensions import db, ma
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
    id = db.Column(db.Integer, primary_key=True, index=True)
    type = db.Column(Enum(CompoundPropertyType))
    value = db.Column(db.String(100))

    def __repr__(self):
        return f"<CpdProperty {self.type}: {self.value}>"


class Compound(db.Model):
    __tablename__ = "compound"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    property_id = db.Column(db.ForeignKey("compound_property.id"))
    name = db.Column(db.String(100))
    bcs = db.Column(db.String(100))
    comment = db.Column(db.Text())

    def __repr__(self):
        return f"<Compound {self.name}>"



