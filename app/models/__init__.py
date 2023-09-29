from app import db
from sqlalchemy.ext.associationproxy import association_proxy

from .cell import Cell
from .compound import Compound, CompoundProperty, CompoundPropertyType
from .item import Item, Tag, ItemTagAssociation
from .modality import Modality
from .plate import Plate
from .section import Section
from .stack import Stack, StackModalityAssociation
from .timepoint import TimePoint

Plate.items = db.relationship("Item")
Plate.sections = db.relationship("Section")
Item.plate = db.relationship(
    "Plate", back_populates="items", foreign_keys=[Item.plate_id]
)

TimePoint.items = db.relationship("Item")
Cell.sections = db.relationship("Section")
Compound.sections = db.relationship("Section")
Plate.timepoints = db.relationship("TimePoint", cascade='all, delete')
Stack.sections = db.relationship("Section")
Stack.stack_modality_assoc = db.relationship("StackModalityAssociation")
Modality.stack_modality_assoc = db.relationship("StackModalityAssociation")


Item.timepoint = db.relationship(
    "TimePoint", back_populates="items", foreign_keys=[Item.timepoint_id]
)
Item.item_tag_assoc = db.relationship(
    "ItemTagAssociation",
    back_populates="item",
)

Item.tags = association_proxy("item_tag_assoc", "tag")

TimePoint.plate = db.relationship(
    "Plate", back_populates="timepoints", foreign_keys=[TimePoint.plate_id]
)


Section.plate = db.relationship(
    "Plate", back_populates="sections", foreign_keys=[Section.plate_id]
)
Section.cell = db.relationship(
    "Cell", back_populates="sections", foreign_keys=[Section.cell_id]
)
Section.compound = db.relationship(
    "Compound", back_populates="sections", foreign_keys=[Section.compound_id]
)
Section.stack = db.relationship(
    "Stack", back_populates="sections", foreign_keys=[Section.stack_id]
)

Stack.modalities = association_proxy("stack_modality_assoc", "modality")
Stack.channels = association_proxy("stack_modality_assoc", "chan")

StackModalityAssociation.stack = db.relationship(
    Stack,
    back_populates="stack_modality_assoc",
    foreign_keys=[StackModalityAssociation.stack_id],
)
StackModalityAssociation.modality = db.relationship(
    "Modality",
    back_populates="stack_modality_assoc",
    foreign_keys=[StackModalityAssociation.modality_id],
)


Compound.props = db.relationship(
    "CompoundProperty", foreign_keys=[Compound.property_id]
)
Modality.stacks = association_proxy("stack_modality_assoc", "stack")
