#!/usr/bin/env python3

from flask_smorest import Blueprint
from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import abort

from ... import db
from ... import models as mdl
from ... import schemas as sch
from .utils import admin_required

blp = Blueprint(
    "Section",
    "Section",
    url_prefix="/api/v1",
    description="Spatially contiguous subset of wells in a plate",
)


def range_subset(range1, range2):
    """Whether range1 is a subset of range2."""
    if not range1:
        return True  # empty range is subset of anything
    if not range2:
        return False  # non-empty range can't be subset of empty range
    if len(range1) > 1 and range1.step % range2.step:
        return False  # must have a single value or integer multiple step
    return range1.start in range2 and range1[-1] in range2


def make_grid(row_start, row_end, col_start, col_end, *args, **kwargs):
    row_range = [i for i in range(ord(row_start), ord(row_end) + 1)]
    col_range = [i for i in range(col_start, col_end + 1)]
    coordinates = [(r, c) for r in row_range for c in col_range]
    return coordinates


def create_section(data):
    record_exists(db, mdl.Cell, value=data["cell_id"], field="id")
    record_exists(db, mdl.Compound, value=data["compound_id"], field="id")

    Section._check_range(data["plate_id"], data)

    # check for overlap with existing sections of same plate
    existing_sections = (
        db.session.query(mdl.Plate).filter_by(id=data["plate_id"]).first().sections
    )
    for s in existing_sections:
        Section._check_overlap(s.__dict__, data)

    section = mdl.Section(**data)
    db.session.add(section)
    db.session.commit()

    return section

def delete_section(id):
    res = record_exists(db, mdl.Section, id, field="id").first()

    db.session.delete(res)
    db.session.commit()

def update_section(id, data):
    if "cell_code" in data.keys():
        data["cell_id"] = (
            record_exists(db, mdl.Cell, value=data["cell_code"], field="code")
            .first()
            .id
        )
        data.pop("cell_code", None)
    if "compound_name" in data.keys():
        data["compound_id"] = (
            record_exists(db, mdl.Compound, value=data["compound_name"], field="name")
            .first()
            .id
        )
        data.pop("compound_name", None)
    if "stack_name" in data.keys():
        data["stack_id"] = (
            record_exists(db, mdl.Stack, value=data["stack_name"], field="name")
            .first()
            .id
        )
        data.pop("stack_name", None)

    elem = db.session.query(mdl.Section).filter_by(id=id)

    if data:
        elem.update(data)
        db.session.commit()
    return elem


@blp.route("/sections/<uuid:id>")
class Section(MethodView):
    @blp.response(200, sch.SectionSchema)
    def get(self, id):
        """Get section"""

        res = record_exists(db, mdl.Section, id)

        return res.first()

    @admin_required
    @blp.arguments(sch.SectionSchema)
    @blp.response(200, sch.SectionSchema)
    def patch(self, update_data, id):
        """Update section"""
        res = update_section(id, update_data).first()

        return res

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete section"""

        res = delete_section(id)

    @staticmethod
    def _check_range(plate_id, a):
        """
        check that requested range contained in a matches available range of plate with ID timepoint_id

        a: dicts that contain keys row_start, row_end, col_start, col_end
        """

        # get row and col range of plate
        plate = db.session.query(mdl.Plate).filter_by(id=a["plate_id"]).first()
        items = plate.items
        rows = [im.row for im in items]
        cols = [im.col for im in items]
        row_range = range(ord(min(rows)), ord(max(rows)))
        col_range = range(min(cols), max(cols))

        # compare with requested range
        if not range_subset(
            range(ord(a["row_start"]), ord(a["row_end"])), row_range
        ) and range_subset(range(a["col_start"], a["col_end"]), col_range):
            abort(
                409,
                message="Requested section is out of bounds for plate with id {} within rows: {}, cols: {}.".format(
                    plate_id,
                    (chr(row_range.start), chr(row_range.stop)),
                    (col_range.start, col_range.stop),
                ),
            )

    @staticmethod
    def _check_overlap(a, b):
        """
        check if new section overlaps existing sections

        a, b: dicts that contain keys row_start, row_end, col_start, col_end
        """
        section_coords = make_grid(**a)
        new_section_coords = make_grid(**b)

        if set(section_coords) & set(new_section_coords):
            abort(409, message="Requested section overlaps with existing section.")
