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
    def put(self, update_data, id):
        """Update plate"""
        res = PlateAPI._update(id, update_data)

        return res

    @admin_required
    @blp.response(204, PlateSchema)
    def delete(self, id):
        """Delete plate"""

        res = PlateAPI._delete(id)

    @admin_required
    @blp.arguments(PlateSchema)
    @blp.response(200, PlateSchema)
    def patch(self, update_data, id):
        """Patch plate"""
        res = PlateAPI._update(id, update_data)

        return res

    @staticmethod
    def _create(data):
        check_duplicate(db.session, Plate, name=data["name"])

        for timepoint in data["timepoints"]:
            check_duplicate(db.session, TimePoint, uri=timepoint["uri"])

        timepoints = data.pop("timepoints")

        plate = Plate(**data)
        db.session.add(plate)
        db.session.commit()

        for timepoint in timepoints:
            tp = TimePoint(**timepoint, plate_id=plate.id)
            db.session.add(tp)
            db.session.commit()

            items = loader(timepoint["uri"])
            items = [Item(**item, plate_id=plate.id, timepoint_id=tp.id,
                          ) for item in items]
            db.session.add_all(items)
            db.session.commit()

        return plate

    @staticmethod
    def _update(id, data):
        res = record_exists(Plate, id)

        q = Plate.query.filter_by(id=id)
        q.update(data)
        db.session.commit()

        return q.first()

    @staticmethod
    def _delete(id):
        """Delete plate and all associated objects."""

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
    def post(self, new_data):
        """Add a new plate"""

        res = PlateAPI._create(new_data)

        return res
