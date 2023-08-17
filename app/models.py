#!/usr/bin/env python3
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.sql import func
from sqlalchemy_mptt.mixins import BaseNestedSets
import enum
from sqlalchemy import Enum

from . import db

from sqlalchemy_utils.types.uuid import UUIDType
import uuid

__all__ = ["cell", "compound", "tag", "section", "plate", "modality", "stack"]


class Section(db.Model):
    """
    Define a section, i.e. a set of spatially-organized wells
    contained within a plate.

    the *_start and *_end attribute define the location range along rows and columns.
    We force a section to contain a SINGLE cell and a SINGLE stack configuration.

    """

    __tablename__ = "section"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)

    col_start = db.Column(db.Integer)
    col_end = db.Column(db.Integer)
    row_start = db.Column(db.String(1))
    row_end = db.Column(db.String(1))
    compound_concentration = db.Column(db.Float)

    plate_id = db.Column(db.ForeignKey("plate.id"))
    cell_id = db.Column(db.ForeignKey("cell.id"))
    compound_id = db.Column(db.ForeignKey("compound.id"))
    stack_id = db.Column(db.ForeignKey("stack.id"))

    plate = db.relationship("Plate", back_populates="sections", foreign_keys=[plate_id])
    cell = db.relationship("Cell", back_populates="sections", foreign_keys=[cell_id])
    compound = db.relationship(
        "Compound", back_populates="sections", foreign_keys=[compound_id]
    )
    stack = db.relationship("Stack", back_populates="sections", foreign_keys=[stack_id])

    def __repr__(self):
        return f"<Section {self.id}>"


class Item(db.Model):
    """
    Basic object that refers to a resource (file)
    """

    __tablename__ = "item"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    uri = db.Column(db.String(300))
    plate_id = db.Column(db.ForeignKey("plate.id"))
    plate = db.relationship("Plate", back_populates="items", foreign_keys=[plate_id])
    timepoint_id = db.Column(db.ForeignKey("timepoint.id"))
    timepoint = db.relationship(
        "TimePoint", back_populates="items", foreign_keys=[timepoint_id]
    )
    row = db.Column(db.String(1))
    col = db.Column(db.Integer)
    site = db.Column(db.Integer)
    chan = db.Column(db.Integer)
    item_tag_assoc = db.relationship(
        "ItemTagAssociation",
        back_populates="item",
    )

    tags = association_proxy("item_tag_assoc", "tag")


class Stack(db.Model):
    """
    This allows to group different modalities
    """

    __tablename__ = "stack"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    comment = db.Column(db.Text())

    sections = db.relationship(
        "Section", back_populates="stack", foreign_keys="Section.stack_id"
    )

    # Use transition table here to set channel for each modality
    stack_modality_assoc = db.relationship(
        "StackModalityAssociation",
        back_populates="stack",
    )
    modalities = association_proxy("stack_modality_assoc", "modality")
    channels = association_proxy("stack_modality_assoc", "chan")

    def __repr__(self):
        return f"<Stack{self.name}>"


class Modality(db.Model):
    __tablename__ = "modality"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    target = db.Column(db.String(100))
    comment = db.Column(db.Text())

    stack_modality_assoc = db.relationship(
        "StackModalityAssociation",
        back_populates="modality",
    )
    stacks = association_proxy("stack_modality_assoc", "stack")

    def __repr__(self):
        return f"<Modality {self.name}>"


class StackModalityAssociation(db.Model):
    """
    Association model between stack and modality.
    Allows to set regular expression to match file name
    """

    __tablename__ = "stack_modality_assoc"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    stack_id = db.Column(db.ForeignKey("stack.id"), primary_key=True)
    modality_id = db.Column(db.ForeignKey("modality.id"), primary_key=True)
    chan = db.Column(db.Integer())

    stack = db.relationship(
        Stack, back_populates="stack_modality_assoc", foreign_keys=[stack_id]
    )
    modality = db.relationship("Modality", foreign_keys=[modality_id])


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    comment = db.Column(db.Text())

    def __repr__(self):
        return f"<Tag {self.name}>"


class ItemTagAssociation(db.Model):
    """
    Association model between item and tag.
    """

    __tablename__ = "item_tag_assoc"
    __table_args__ = (db.UniqueConstraint("item_id", "tag_id"),)
    item_id = db.Column(db.ForeignKey("item.id"), primary_key=True)
    tag_id = db.Column(db.ForeignKey("tag.id"), primary_key=True)

    item = db.relationship("Item", foreign_keys=[item_id])
    tag = db.relationship("Tag", foreign_keys=[tag_id])


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

    sections = db.relationship(
        "Section", back_populates="compound", foreign_keys="Section.compound_id"
    )
    props = db.relationship("CompoundProperty", foreign_keys=[property_id])

    def __repr__(self):
        return f"<Compound {self.name}>"


class Cell(db.Model):
    __tablename__ = "cell"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    code = db.Column(db.String(100))
    sections = db.relationship(
        "Section", back_populates="cell", foreign_keys="Section.cell_id"
    )

    def __repr__(self):
        return f"<Cell {self.name}>"


class Plate(db.Model):
    __tablename__ = "plate"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    origin = db.Column(db.String(100))
    comment = db.Column(db.Text())

    # relations
    sections = db.relationship(
        "Section", back_populates="plate", foreign_keys="Section.plate_id"
    )
    timepoints = db.relationship(
        "TimePoint", back_populates="plate", foreign_keys="TimePoint.plate_id"
    )
    items = db.relationship("Item", back_populates="plate", foreign_keys=Item.plate_id)

    def __repr__(self):
        return f"<Plate {self.name} ({self.id})>"


class TimePoint(db.Model):
    __tablename__ = "timepoint"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    uri = db.Column(db.String(300))
    plate_id = db.Column(db.ForeignKey("plate.id"))
    plate = db.relationship(
        "Plate", back_populates="timepoints", foreign_keys=[plate_id]
    )
    items = db.relationship(
        "Item", back_populates="timepoint", foreign_keys=Item.timepoint_id
    )

    def __repr__(self):
        return f"<TimePoint {self.uri} ({self.id})>"
