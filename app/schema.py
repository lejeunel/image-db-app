#!/usr/bin/env python3
import marshmallow as ma
from app.utils import record_exists
from .config import default as cfg
from .models import Stack, Cell, Compound

class ItemsSchema(ma.Schema):

    id = ma.fields.UUID(ignore_dump=True)
    uri = ma.fields.String()
    row = ma.fields.String()
    col = ma.fields.Int()
    site = ma.fields.Int()
    plate_name = ma.fields.String()
    cell_name = ma.fields.String()
    cell_code = ma.fields.String()
    stack_name = ma.fields.String()
    modality_name = ma.fields.String()
    modality_target = ma.fields.String()
    compound_concentration = ma.fields.Float()
    compound_name = ma.fields.String()
    compound_target = ma.fields.String()
    compound_moa_group = ma.fields.String()
    compound_moa_subgroup = ma.fields.String()
    tp_time = ma.fields.DateTime()
    timepoint_id = ma.fields.UUID()
    section_id = ma.fields.UUID()
    plate_id = ma.fields.UUID()
    tags = ma.fields.String()

class TimePointSchema(ma.Schema):
    class Meta:
        ordered = True

    id = ma.fields.UUID(dump_only=True)
    uri = ma.fields.String()
    time = ma.fields.DateTime()


class PlateSchema(ma.Schema):
    class Meta:
        ordered = True

    id = ma.fields.UUID(dump_only=True)
    name = ma.fields.String()
    date = ma.fields.DateTime()
    origin = ma.fields.String()
    timepoints = ma.fields.List(ma.fields.Nested(TimePointSchema))
    project = ma.fields.String()
    comment = ma.fields.String()

    capture_regexp = ma.fields.Dict(keys=ma.fields.Str(), values=ma.fields.String(),
                                    load_default=cfg.CAPTURE_REGEXP_DICT)
    ignore_regexp = ma.fields.String(load_default=cfg.IGNORE_REGEXP)
    valid_regexp = ma.fields.String(load_default=cfg.VALID_REGEXP)


class CellSchema(ma.Schema):
    class Meta:
        ordered = True

    id = ma.fields.UUID(dump_only=True)
    name = ma.fields.String()
    code = ma.fields.String()


class CompoundSchema(ma.Schema):
    class Meta:
        ordered = True

    id = ma.fields.UUID(dump_only=True)
    name = ma.fields.String()
    moa_group = ma.fields.String()
    moa_subgroup = ma.fields.String()
    target = ma.fields.String()
    comment = ma.fields.String()
    bcs = ma.fields.String()

class SectionSchema(ma.Schema):
    class Meta:
        ordered = True

    id = ma.fields.UUID(dump_only=True)
    col_start = ma.fields.Int()
    col_end = ma.fields.Int()
    row_start = ma.fields.String()
    row_end = ma.fields.String()
    stack_name = ma.fields.String()
    cell_code = ma.fields.String()
    compound_name = ma.fields.String()
    compound_concentration = ma.fields.Float()

    @ma.post_dump()
    def stack_id_to_name(self, data, **kwargs):
        if "stack_id" in data:
            data["stack_name"] = (
                Stack.query.filter(Stack.id == data["stack_id"]).first().name
            )
            data.pop("stack_id")
        return data

    @ma.post_load()
    def stack_name_to_id(self, data, **kwargs):
        if "stack_name" in data:
            data["stack_id"] = (
                Stack.query.filter(Stack.name == data["stack_name"]).first().id
            )
            data.pop("stack_name")
        return data

    @ma.post_dump()
    def cell_id_to_code(self, data, **kwargs):
        if "cell_id" in data:
            data["cell_code"] = (
                Cell.query.filter(Cell.id == data["cell_id"]).first().code
            )
            data.pop("cell_id")
        return data

    @ma.post_load()
    def cell_code_to_id(self, data, **kwargs):
        if "cell_code" in data:
            data["cell_id"] = (
                Cell.query.filter(Cell.code == data["cell_code"]).first().id
            )
            data.pop("cell_code")
        return data

    @ma.post_dump()
    def compound_id_to_name(self, data, **kwargs):
        if "compound_id" in data:
            data["compound_name"] = (
                Compound.query.filter(Compound.id == data["compound_id"]).first().name
            )
            data.pop("compound_id")
        return data

    @ma.post_load()
    def compound_name_to_id(self, data, **kwargs):
        if "compound_name" in data:
            data["compound_id"] = (
                Compound.query.filter(Compound.name == data["compound_name"]).first().id
            )
            data.pop("compound_name")
        return data

    @ma.pre_load()
    def check_records(self, data, **kwargs):
        if "stack_name" in data:
            record_exists(Stack, value=data["stack_name"], field="name")
        if "compound_name" in data:
            record_exists(Compound, value=data["compound_name"], field="name")
        if "cell_code" in data:
            record_exists(Cell, value=data["cell_code"], field="code")

        return data

class StackSchema(ma.Schema):
    class Meta:
        ordered = True

    id = ma.fields.UUID(dump_only=True)
    name = ma.fields.String()
    comment = ma.fields.String()
    modalities = ma.fields.List(ma.fields.String())
    regexps = ma.fields.List(ma.fields.String())
