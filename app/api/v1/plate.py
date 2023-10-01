#!/usr/bin/env python3

from app.extensions import db
from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint
from flask import jsonify

from ... import models as mdl
from ... import schemas as sch
from .section import create_section, delete_section
from .timepoint import create_timepoint
from .utils import admin_required, check_duplicate
from ...exceptions import MyException

blp = Blueprint("Plate", "Plate", url_prefix="/api/v1/plates", description="Main collection. Contains sub-resources Section, and TimePoint")

@blp.errorhandler(MyException)
def parsing_exception(e):
    return jsonify(e.to_dict()), e.status_code

@blp.route("/<uuid:id>/timepoints")
class TimePointsOfPlate(MethodView):
    @blp.response(200, sch.TimePointSchema(many=True))
    def get(self, id):
        """Get all timepoints from plate ID"""

        res = record_exists(db, mdl.Plate, id)

        return res.first().timepoints

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete all timepoints"""

        res = record_exists(db, mdl.Plate, id)
        for tp in res.first().timepoints:
            db.session.delete(tp)

    @admin_required
    @blp.arguments(sch.TimePointSchema)
    @blp.response(201, sch.TimePointSchema)
    def post(self, data, id):
        """Add a new timepoint"""

        data["plate_id"] = id
        res = create_timepoint(data)

        return res

@blp.route('/<uuid:id>/stack')
@blp.response(200, sch.StackSchema())
def get_stack(id):
    res = record_exists(db, mdl.Plate, id)

    return res.first().stack

@blp.route("/<uuid:id>/sections")
class SectionsOfPlate(MethodView):
    @blp.response(200, sch.SectionSchema(many=True))
    def get(self, id):
        """Get all sections from plate ID"""

        res = record_exists(db, mdl.Plate, id)

        return res.first().sections

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete all sections"""

        res = record_exists(db, mdl.Plate, id)
        for s in res.first().sections:
            res = delete_section(s.id)

    @admin_required
    @blp.arguments(sch.SectionSchema)
    @blp.response(201, sch.SectionSchema)
    def post(self, data, id):
        """Add a new section"""

        data["plate_id"] = id
        res = create_section(data)

        return res


@blp.route("/<uuid:id>")
class Plate(MethodView):
    model = mdl.Plate

    @blp.response(200, sch.PlateSchema)
    def get(self, id):
        """Get plate"""

        res = record_exists(db, mdl.Plate, id)

        return res.first()

    @admin_required
    @blp.arguments(sch.PlateSchema)
    @blp.response(200, sch.PlateSchema)
    def patch(self, data, id):
        """Update plate."""
        q = record_exists(db, mdl.Plate, id)
        q.update(data)
        db.session.commit()

        return q.first()

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete plate"""

        res = record_exists(db, mdl.Plate, id)

        db.session.delete(res.first())

        db.session.commit()



@blp.route("/")
class Plates(MethodView):
    @blp.response(200, sch.PlateSchema(many=True))
    def get(self):
        """Get all plates"""

        plate = mdl.Plate.query.all()
        return plate

    @admin_required
    @blp.arguments(sch.PlateSchema)
    @blp.response(201, sch.PlateSchema)
    def post(self, data):
        """Add a new plate"""

        check_duplicate(db.session, mdl.Plate, name=data["name"])

        plate = mdl.Plate(**data)

        db.session.add(plate)
        db.session.commit()

        return plate
