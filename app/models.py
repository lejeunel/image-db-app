#!/usr/bin/env python3
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from flask import current_app

from . import db, app

from sqlalchemy_utils.types.uuid import UUIDType
import uuid

__all__ = ["cell", "compound", "tag", "section", "plate", "modality", "stack"]


class Object(db.Model):
    __tablename__ = "object"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    project = db.Column(db.String(100))
    object_type = db.Column(db.String(32), nullable=False)
    __mapper_args__ = {"polymorphic_on": object_type}


class Section(Object):
    """
    Define a section, i.e. a set of spatially-organized wells
    contained within a plate.

    the *_start and *_end attribute define the location range along rows and columns.
    We force a section to contain a SINGLE cell and a SINGLE stack configuration.

    """

    __tablename__ = "section"
    id = db.Column(None, db.ForeignKey("object.id"), primary_key=True)

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

    __mapper_args__ = {"polymorphic_identity": "section"}

    def __repr__(self):
        return f"<Section {self.id}>"


class Item(Object):
    """
    Basic object that refers to a resource (file)
    """
    __tablename__ = "item"
    id = db.Column(None, db.ForeignKey("object.id"), primary_key=True)
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
    item_tag_assoc = db.relationship(
        "ItemTagAssociation",
        back_populates="item",
    )

    tags = association_proxy("item_tag_assoc", "tag")
    __mapper_args__ = {"polymorphic_identity": "item"}


class Stack(Object):
    """
    This allows to group different modalities
    """

    __tablename__ = "stack"
    id = db.Column(None, db.ForeignKey("object.id"), primary_key=True)
    name = db.Column(db.String(100))
    comment = db.Column(db.Text())

    sections = db.relationship(
        "Section", back_populates="stack", foreign_keys="Section.stack_id"
    )

    # Use transition table here to set regexp for each modality
    stack_modality_assoc = db.relationship(
        "StackModalityAssociation",
        back_populates="stack",
    )
    modalities = association_proxy("stack_modality_assoc", "modality")
    regexps = association_proxy("stack_modality_assoc", "regexp")

    __mapper_args__ = {"polymorphic_identity": "stack"}

    def __repr__(self):
        return f"<Stack{self.name}>"


class Modality(Object):
    __tablename__ = "modality"
    id = db.Column(None, db.ForeignKey("object.id"), primary_key=True)
    name = db.Column(db.String(100))
    target = db.Column(db.String(100))
    comment = db.Column(db.Text())

    stack_modality_assoc = db.relationship(
        "StackModalityAssociation",
        back_populates="modality",
    )
    stacks = association_proxy("stack_modality_assoc", "stack")

    __mapper_args__ = {"polymorphic_identity": "modality"}

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
    regexp = db.Column(db.String(50))

    stack = db.relationship(
        Stack, back_populates="stack_modality_assoc", foreign_keys=[stack_id]
    )
    modality = db.relationship("Modality", foreign_keys=[modality_id])


class Tag(Object):
    __tablename__ = "tag"
    id = db.Column(None, db.ForeignKey("object.id"), primary_key=True)
    name = db.Column(db.String(100))
    comment = db.Column(db.Text())
    __mapper_args__ = {"polymorphic_identity": "tag"}

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


class Compound(Object):
    __tablename__ = "compound"
    id = db.Column(None, db.ForeignKey("object.id"), primary_key=True)
    name = db.Column(db.String(100))
    moa_group = db.Column(db.String(100))
    moa_subgroup = db.Column(db.String(100))
    target = db.Column(db.String(100))
    bcs = db.Column(db.String(100))
    comment = db.Column(db.Text())

    sections = db.relationship(
        "Section", back_populates="compound", foreign_keys="Section.compound_id"
    )
    __mapper_args__ = {"polymorphic_identity": "compound"}

    def __repr__(self):
        return f"<Compound {self.name}>"


class Cell(Object):
    __tablename__ = "cell"
    id = db.Column(None, db.ForeignKey("object.id"), primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(100))
    sections = db.relationship(
        "Section", back_populates="cell", foreign_keys="Section.cell_id"
    )
    __mapper_args__ = {"polymorphic_identity": "cell"}

    def __repr__(self):
        return f"<Cell {self.name}>"


class Plate(Object):
    __tablename__ = "plate"
    id = db.Column(None, db.ForeignKey("object.id"), primary_key=True)
    name = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    origin = db.Column(db.String(100))
    comment = db.Column(db.Text())

    # set regular expression to extract row, column and site coordinates
    row_regexp = db.Column(db.String(100))
    col_regexp = db.Column(db.String(100))
    site_regexp = db.Column(db.String(100))
    ignore_regexp = db.Column(db.String(100))
    valid_regexp = db.Column(db.String(100))

    # relations
    sections = db.relationship(
        "Section", back_populates="plate", foreign_keys="Section.plate_id"
    )
    timepoints = db.relationship(
        "TimePoint", back_populates="plate", foreign_keys="TimePoint.plate_id"
    )
    items = db.relationship(
        "Item", back_populates="plate", foreign_keys=Item.plate_id
    )

    __mapper_args__ = {"polymorphic_identity": "plate"}

    def __init__(self, **kwargs):
        super().__init__(row_regexp=current_app.config['ROW_REGEXP'],
                 col_regexp=current_app.config['COL_REGEXP'],
                 site_regexp=current_app.config['SITE_REGEXP'],
                 ignore_regexp=current_app.config['IGNORE_REGEXP'],
                 valid_regexp=current_app.config['VALID_REGEXP'], **kwargs)


    def __repr__(self):
        return f"<Plate {self.name} ({self.id})>"


class TimePoint(Object):
    __tablename__ = "timepoint"
    id = db.Column(None, db.ForeignKey("object.id"), primary_key=True)
    time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    uri = db.Column(db.String(300))
    plate_id = db.Column(db.ForeignKey("plate.id"))
    plate = db.relationship(
        "Plate", back_populates="timepoints", foreign_keys=[plate_id]
    )
    items = db.relationship(
        "Item", back_populates="timepoint", foreign_keys=Item.timepoint_id
    )

    __mapper_args__ = {"polymorphic_identity": "timepoint"}

    def __repr__(self):
        return f"<TimePoint {self.uri} ({self.id})>"
