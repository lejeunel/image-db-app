#!/usr/bin/env python3

import marshmallow as ma
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db
from ...models.cell import Cell, CellSchema
from . import (
    admin_required,
    check_dependencies,
    check_duplicate,
)
from app.utils import record_exists

blp = Blueprint("Cell", "Cell", url_prefix="/api/v1/cell", description="")


@blp.route("/<uuid:id>")
class CellAPI(MethodView):
    model = Cell

    @blp.response(200, CellSchema)
    def get(self, id):
        """Get cell"""

        res = record_exists(Cell, id).first()
        return res

    @admin_required
    @blp.arguments(CellSchema)
    @blp.response(200, CellSchema)
    def put(self, update_data, id):
        """Update cell"""
        res = CellAPI._update(id, update_data)

        return res

    @admin_required
    @blp.arguments(CellSchema)
    @blp.response(200, CellSchema)
    def patch(self, update_data, id):
        """Patch compound"""
        res = CellAPI._update(id, update_data)

        return res

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete cell"""
        cell = record_exists(Cell, id)
        check_dependencies(Cell, value=id, field="id", remote="sections")

        db.session.delete(cell.first())
        db.session.commit()

    @staticmethod
    def _create(data):

        check_duplicate(db.session, Cell, code=data["code"])
        check_duplicate(db.session, Cell, name=data["name"])

        cell = Cell(**data)

        db.session.add(cell)
        db.session.commit()
        return cell

    @staticmethod
    def _update(id, data):

        cell = record_exists(Cell, id)

        cell.update(data)
        db.session.commit()
        return cell.first()


@blp.route("/")
class CellsAPI(MethodView):
    @blp.response(200, CellSchema(many=True))
    def get(self):
        """Get all cells"""

        item = Cell.query.all()
        return item

    @admin_required
    @blp.arguments(CellSchema)
    @blp.response(201, CellSchema)
    def post(self, data):
        """Add a new cell"""
        res = CellAPI._create(data)

        return res
