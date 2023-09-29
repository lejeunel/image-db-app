import uuid

from app.extensions import db, ma
from app.models.compound import Compound
from app.models.stack import Stack
from app.utils import record_exists
from marshmallow import post_dump, post_load, pre_load
from sqlalchemy_utils.types.uuid import UUIDType

from .cell import Cell


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

    plate_id = db.Column(UUIDType, db.ForeignKey("plate.id"))
    cell_id = db.Column(UUIDType, db.ForeignKey("cell.id"))
    compound_id = db.Column(UUIDType, db.ForeignKey("compound.id"))
    stack_id = db.Column(UUIDType, db.ForeignKey("stack.id"))


    def __repr__(self):
        return f"<Section {self.id}>"


