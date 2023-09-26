import uuid

from src import db, ma
from src.models.compound import Compound
from src.models.stack import Stack
from src.utils import record_exists
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


class SectionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Section
        include_fk = True
        additional = ('compound_name', 'cell_name', 'cell_code', 'stack_name')

    @post_dump()
    def stack_id_to_name(self, data, **kwargs):
        if "stack_id" in data:
            data["stack_name"] = (
                db.session.query(Stack).filter(Stack.id == data["stack_id"]).first().name
            )
            data.pop("stack_id")
        return data

    @post_load()
    def stack_name_to_id(self, data, **kwargs):
        if "stack_name" in data:
            data["stack_id"] = (
                db.session.query(Stack).filter(Stack.name == data["stack_name"]).first().id
            )
            data.pop("stack_name")
        return data

    @post_dump()
    def cell_id_to_code(self, data, **kwargs):
        if "cell_id" in data:
            data["cell_code"] = (
                db.session.query(Cell).filter(Cell.id == data["cell_id"]).first().code
            )
            data.pop("cell_id")
        return data

    @post_load()
    def cell_code_to_id(self, data, **kwargs):
        if "cell_code" in data:
            data["cell_id"] = (
                db.session.query(Cell).filter(Cell.code == data["cell_code"]).first().id
            )
            data.pop("cell_code")
        return data

    @post_dump()
    def compound_id_to_name(self, data, **kwargs):
        if "compound_id" in data:
            data["compound_name"] = (
                db.session.query(Compound).filter(Compound.id == data["compound_id"]).first().name
            )
            data.pop("compound_id")
        return data

    @post_load()
    def compound_name_to_id(self, data, **kwargs):
        if "compound_name" in data:
            data["compound_id"] = (
                db.session.query(Compound).filter(Compound.name == data["compound_name"]).first().id
            )
            data.pop("compound_name")
        return data

    @pre_load()
    def check_records(self, data, **kwargs):
        if "stack_name" in data:
            record_exists(db, Stack, value=data["stack_name"], field="name")
        if "compound_name" in data:
            record_exists(db,Compound, value=data["compound_name"], field="name")
        if "cell_code" in data:
            record_exists(db,Cell, value=data["cell_code"], field="code")

        return data
