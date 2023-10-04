import enum
import uuid

from app.extensions import db
from sqlalchemy import Enum
from sqlalchemy_mptt.mixins import BaseNestedSets
from sqlalchemy_utils.types.uuid import UUIDType

from .mixins import UpdateMixin


class CompoundPropertyType(enum.IntEnum):
    moa_group = 0
    moa_subgroup = 1
    target = 2


class CompoundProperty(db.Model, BaseNestedSets):
    __tablename__ = "compound_property"
    id = db.Column(db.Integer, primary_key=True, index=True)
    type = db.Column(Enum(CompoundPropertyType), nullable=False)
    value = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<CpdProperty {self.type}: {self.value}>"


class Compound(db.Model, UpdateMixin):
    __tablename__ = "compound"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    property_id = db.Column(db.ForeignKey("compound_property.id"), nullable=False)
    name = db.Column(db.String(100))
    bcs = db.Column(db.String(100))
    comment = db.Column(db.Text())

    def __repr__(self):
        return f"<Compound {self.name}>"



