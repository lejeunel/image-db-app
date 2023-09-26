#!/usr/bin/env python3

from src.utils import record_exists
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db, parser
from ...exceptions import MyException
from ...models.plate import Plate
from ...models.timepoint import TimePoint
from ...models.item import ItemTagAssociation

from ...models.plate import PlateSchema
from . import admin_required, check_duplicate

blp = Blueprint("Plate", "Plate", url_prefix="/api/v1/plate", description="")

@blp.errorhandler(MyException)
def parsing_exception(e):
    return jsonify(e.to_dict()), e.status_code


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
        """Update plate. This does not modify timepoints!"""
        data.pop('timepoints', None)
        res = record_exists(db,Plate, id)

        q = db.session.query(Plate).filter_by(id=id)
        q.update(data)
        db.session.commit()

        return q.first()

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete plate"""

        res = record_exists(db,Plate, id)

        plate = res.first()
        timepoints = plate.timepoints
        sections = plate.sections
        items = plate.items

        tag_assocs = []
        for item in items:
            assoc = db.session.query(ItemTagAssociation).filter(
                ItemTagAssociation.item_id == item.id
            )
            tag_assocs += assoc.all()

        for item in [plate] + timepoints + sections + tag_assocs + items:
            db.session.delete(item)

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

        for timepoint in data["timepoints"]:
            check_duplicate(db.session, TimePoint, uri=timepoint["uri"])

        timepoints = data.pop('timepoints')
        timepoints = [TimePoint(**t) for t in timepoints]

        plate = Plate(**data)

        db.session.add_all(timepoints)
        db.session.add(plate)
        db.session.commit()

        for t in timepoints:
            items = parser(base_uri=t.uri, plate_id=plate.id, timepoint_id=t.id)
            db.session.add_all(items)

        return plate
