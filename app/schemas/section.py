#!/usr/bin/env python3
from app import db, ma
from app.utils import record_exists
from marshmallow import post_dump, post_load, pre_load

from .. import models as mdl


class SectionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = mdl.Section
        include_fk = True
        additional = ("compound_name", "cell_name", "cell_code", "stack_name")

    @post_dump()
    def cell_id_to_code(self, data, **kwargs):
        if "cell_id" in data:
            data["cell_code"] = (
                db.session.query(mdl.Cell)
                .filter(mdl.Cell.id == data["cell_id"])
                .first()
                .code
            )
            data.pop("cell_id")
        return data

    @post_load()
    def cell_code_to_id(self, data, **kwargs):
        if "cell_code" in data:
            data["cell_id"] = (
                db.session.query(mdl.Cell)
                .filter(mdl.Cell.code == data["cell_code"])
                .first()
                .id
            )
            data.pop("cell_code")
        return data

    @post_dump()
    def compound_id_to_name(self, data, **kwargs):
        if "compound_id" in data:
            data["compound_name"] = (
                db.session.query(mdl.Compound)
                .filter(mdl.Compound.id == data["compound_id"])
                .first()
                .name
            )
            data.pop("compound_id")
        return data

    @post_load()
    def compound_name_to_id(self, data, **kwargs):
        if "compound_name" in data:
            data["compound_id"] = (
                db.session.query(mdl.Compound)
                .filter(mdl.Compound.name == data["compound_name"])
                .first()
                .id
            )
            data.pop("compound_name")
        return data

    @pre_load()
    def check_records(self, data, **kwargs):
        if "stack_name" in data:
            record_exists(db, mdl.Stack, value=data["stack_name"], field="name")
        if "compound_name" in data:
            record_exists(db, mdl.Compound, value=data["compound_name"], field="name")
        if "cell_code" in data:
            record_exists(db, mdl.Cell, value=data["cell_code"], field="code")

        return data
