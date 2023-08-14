#!/usr/bin/env python3
import re

from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import current_app

from ... import db, app, loader
from ...models import Item, ItemTagAssociation, Plate, TimePoint
from ...schema import PlateSchema
from . import admin_required, check_duplicate
from ...reader.s3 import S3Reader
from ...batch_loader import BatchLoader

blp = Blueprint("Plate", "Plate", url_prefix="/api/v1/plate", description="")


@blp.route("/<uuid:id>")
class PlateAPI(MethodView):
    model = Plate

    @blp.response(200, PlateSchema)
    def get(self, id):
        """Get plate"""

        res = record_exists(Plate, id)

        return res.first()

    @admin_required
    @blp.arguments(PlateSchema)
    @blp.response(200, PlateSchema)
    def put(self, data, id):
        """Update plate"""
        data.pop('timepoints', None)
        res = record_exists(Plate, id)

        q = Plate.query.filter_by(id=id)
        q.update(data)
        db.session.commit()

        return q.first()

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete plate"""

        res = record_exists(Plate, id)

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

    @admin_required
    @blp.arguments(PlateSchema)
    @blp.response(200, PlateSchema)
    def patch(self, update_data, id):
        """Patch plate"""
        res = PlateAPI._update(id, update_data)

        return res



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

        loader(plate, timepoints)


        return plate
