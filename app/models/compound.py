from sqlalchemy_mptt.mixins import BaseNestedSets
import enum
from sqlalchemy import Enum
import uuid

from app import db, ma
from sqlalchemy_utils.types.uuid import UUIDType

class CompoundPropertyType(enum.Enum):
    moa_group = 1
    moa_subgroup = 2
    target = 3


class CompoundProperty(db.Model, BaseNestedSets):
    __tablename__ = "compound_property"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(Enum(CompoundPropertyType))
    name = db.Column(db.String(100))

    def __repr__(self):
        return f"<CpdProperty {self.type._name_}: {self.name}>"


class Compound(db.Model):
    __tablename__ = "compound"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    property_id = db.Column(db.ForeignKey("compound_property.id"), primary_key=True)
    name = db.Column(db.String(100))
    bcs = db.Column(db.String(100))
    comment = db.Column(db.Text())

    def __repr__(self):
        return f"<Compound {self.name}>"



class CompoundSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Compound

    property_id = ma.Int(required=False)

class CompoundPropertySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CompoundProperty
