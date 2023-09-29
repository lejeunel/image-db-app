#!/usr/bin/env python3

from app.utils import record_exists
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db, parser
from ...exceptions import MyException
from ...models.plate import Plate
from ...models.timepoint import TimePoint, TimePointSchema
from ...models.item import ItemTagAssociation

from ...models.plate import PlateSchema
from . import admin_required, check_duplicate

blp = Blueprint("Plate", "Plate", url_prefix="/api/v1/plate", description="")

@blp.errorhandler(MyException)
def parsing_exception(e):
    return jsonify(e.to_dict()), e.status_code

@blp.route('/<uuid:id>/timepoints')
@blp.response(200, TimePointSchema(many=True))
def get_timepoints(id):
    res = record_exists(db,Plate, id)

    return res.first().timepoints

@blp.route("/<uuid:id>")
class PlateAPI(MethodView):
    model = Plate

    @blp.response(200, PlateSchema)
    def get(self, id):
        """Get plate"""

        res = record_exists(db,Plate, id)

        return res.first()

    @admin_required
    @blp.arguments(PlateSchema)
    @blp.response(200, PlateSchema)
    def patch(self, data, id):
        """Update plate."""
        q = record_exists(db,Plate, id)
        q.update(data)
        db.session.commit()

        return q.first()

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete plate"""

        res = record_exists(db,Plate, id)

        db.session.delete(res.first())

        db.session.commit()



@blp.route("/")
class PlatesAPI(MethodView):
    @blp.response(200, PlateSchema(many=True))
    def get(self):
        """Get all plates"""

        plate = Plate.query.all()
        return plate

    @admin_required
    @blp.arguments(PlateSchema)
    @blp.response(201, PlateSchema)
    def post(self, data):
        """Add a new plate"""

        check_duplicate(db.session, Plate, name=data["name"])

        plate = Plate(**data)

        db.session.add(plate)
        db.session.commit()

        return plate
