#!/usr/bin/env python3

from app import models as mdl
from app.schemas.modality import ModalitySchema
from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db
from .utils import admin_required, check_dependencies, check_duplicate

blp = Blueprint(
    "Modality",
    "Modality",
    url_prefix="/modality",
    description="Item modality",
)


@blp.route("/<uuid:id>")
class Modality(MethodView):
    model = mdl.Modality

    @blp.response(200, ModalitySchema)
    def get(self, id):
        """Get modality"""

        res = record_exists(db, self.model, id).first()
        return res

    @admin_required
    @blp.arguments(ModalitySchema)
    @blp.response(200, ModalitySchema)
    def patch(self, update_data, id):
        """Update modality"""

        res = self._update(id, update_data)

        return res

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete modality"""

        res = self._delete(id)

    @staticmethod
    def _create(data):
        check_duplicate(db.session, mdl.Modality, name=data["name"])

        modality = mdl.Modality(**data)
        db.session.add(modality)
        db.session.commit()
        return modality

    @staticmethod
    def _update(id, data):
        item = record_exists(db, mdl.Modality, id)

        item.update(data)
        db.session.commit()
        return item.first()

    @staticmethod
    def _delete(id):
        res = record_exists(db, mdl.Modality, id)

        check_dependencies(mdl.Modality, value=id, field="id", remote="stacks")

        db.session.delete(res.first())
        db.session.commit()


@blp.route("/")
class Modalities(MethodView):
    @blp.response(200, ModalitySchema(many=True))
    def get(self):
        """Get all modalities"""
        item = mdl.Modality.query.all()
        return item

    @admin_required
    @blp.arguments(ModalitySchema)
    @blp.response(201, ModalitySchema)
    def post(self, data):
        """Add a new modality"""
        res = Modality._create(data)

        return res
