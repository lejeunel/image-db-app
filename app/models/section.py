from app import db, ma
from app.utils import record_exists
from app.models.compound import Compound
from app.models.stack import Stack
from sqlalchemy_utils.types.uuid import UUIDType
import uuid
from marshmallow import post_dump, post_load, pre_load, pre_dump
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

    compound_name = ma.String()
    cell_name = ma.String()
    cell_code = ma.String()
    stack_name = ma.String()

    @post_dump()
    def stack_id_to_name(self, data, **kwargs):
        if "stack_id" in data:
            data["stack_name"] = (
                Stack.query.filter(Stack.id == data["stack_id"]).first().name
            )
            data.pop("stack_id")
        return data

    @post_load()
    def stack_name_to_id(self, data, **kwargs):
        if "stack_name" in data:
            data["stack_id"] = (
                Stack.query.filter(Stack.name == data["stack_name"]).first().id
            )
            data.pop("stack_name")
        return data

    @post_dump()
    def cell_id_to_code(self, data, **kwargs):
        if "cell_id" in data:
            data["cell_code"] = (
                Cell.query.filter(Cell.id == data["cell_id"]).first().code
            )
            data.pop("cell_id")
        return data

    @post_load()
    def cell_code_to_id(self, data, **kwargs):
        if "cell_code" in data:
            data["cell_id"] = (
                Cell.query.filter(Cell.code == data["cell_code"]).first().id
            )
            data.pop("cell_code")
        return data

    @post_dump()
    def compound_id_to_name(self, data, **kwargs):
        if "compound_id" in data:
            data["compound_name"] = (
                Compound.query.filter(Compound.id == data["compound_id"]).first().name
            )
            data.pop("compound_id")
        return data

    @post_load()
    def compound_name_to_id(self, data, **kwargs):
        if "compound_name" in data:
            data["compound_id"] = (
                Compound.query.filter(Compound.name == data["compound_name"]).first().id
            )
            data.pop("compound_name")
        return data

    @pre_load()
    def check_records(self, data, **kwargs):
        if "stack_name" in data:
            record_exists(Stack, value=data["stack_name"], field="name")
        if "compound_name" in data:
            record_exists(Compound, value=data["compound_name"], field="name")
        if "cell_code" in data:
            record_exists(Cell, value=data["cell_code"], field="code")

        return data
