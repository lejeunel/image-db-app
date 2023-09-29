#!/usr/bin/env python3

from app.utils import record_exists
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint

from app.extensions import db
from ... import schemas as sch
from ... import models as mdl
from ...exceptions import MyException
from .utils import admin_required, check_duplicate

blp = Blueprint("Plate", "Plate", url_prefix="/api/v1/plate", description="Main collection. Contains sub-resources Section, and TimePoint")

@blp.errorhandler(MyException)
def parsing_exception(e):
    return jsonify(e.to_dict()), e.status_code

@blp.route('/<uuid:id>/timepoints')
@blp.response(200, sch.TimePointSchema(many=True))
def get_timepoints(id):
    res = record_exists(db, mdl.Plate, id)

    return res.first().timepoints

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
