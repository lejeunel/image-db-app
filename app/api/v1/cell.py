#!/usr/bin/env python3

from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db
from ... import schemas as sch
from ... import models as mdl
from .utils import admin_required, check_dependencies, check_duplicate

blp = Blueprint("Cell", "Cell", url_prefix="/api/v1/cells", description="")


@blp.route("/<uuid:id>")
class Cell(MethodView):
    model = mdl.Cell

    @blp.response(200, sch.CellSchema)
    def get(self, id):
        """Get cell"""

        res = record_exists(db, Cell, id).first()
        return res

    @admin_required
    @blp.arguments(sch.CellSchema)
    @blp.response(200, sch.CellSchema)
    def patch(self, update_data, id):
        """Update cell"""
        res = Cell._update(id, update_data)

        return res

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete cell"""
        cell = record_exists(db, mdl.Cell, id)
        check_dependencies(mdl.Cell, value=id, field="id", remote="sections")

        db.session.delete(cell.first())
        db.session.commit()

    @staticmethod
    def _create(data):
        check_duplicate(db.session, mdl.Cell, code=data["code"])
        check_duplicate(db.session, mdl.Cell, name=data["name"])

        cell = mdl.Cell(**data)

        db.session.add(cell)
        db.session.commit()
        return cell

    @staticmethod
    def _update(id, data):
        cell = record_exists(db, mdl.Cell, id)

        cell.update(data)
        db.session.commit()
        return cell.first()


@blp.route("/")
class Cells(MethodView):
    @blp.response(200, sch.CellSchema(many=True))
    def get(self):
        """Get all cells"""

        item = mdl.Cell.query.all()
        return item

    @admin_required
    @blp.arguments(sch.CellSchema)
    @blp.response(201, sch.CellSchema)
    def post(self, data):
        """Add a new cell"""
        res = Cell._create(data)

        return res
