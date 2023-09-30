from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db
from ... import models as mdl
from ... import schemas as sch
from .utils import admin_required

blp = Blueprint(
    "CompoundProperty",
    "CompoundProperty",
    url_prefix="/api/v1/compound-properties",
    description="Properties of chemical compounds",
)

@blp.route("/")
class CompoundProperties(MethodView):
    model = mdl.CompoundProperty

    @blp.response(200, sch.CompoundPropertySchema(many=True))
    def get(self):
        """Get all compound properties"""

        return mdl.CompoundProperty.query.all()

    @admin_required
    @blp.arguments(sch.CompoundPropertySchema)
    @blp.response(201, sch.CompoundPropertySchema)
    def post(self, data):
        """Add a new compound property"""

        prop = mdl.CompoundProperty(**data)
        db.session.add(prop)
        db.session.commit()

        return prop


@blp.route("/<uuid:id>")
class CompoundProperty(MethodView):
    model = mdl.CompoundProperty

    @blp.response(200, sch.CompoundPropertySchema)
    def get(self, id):
        """Get compound property"""

        res = record_exists(db, self.model, id).first()
        return res

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete compound property"""
        res = record_exists(db, self.model, id).first()
        db.session.delete(res)

    @admin_required
    @blp.arguments(sch.CompoundPropertySchema)
    @blp.response(200, sch.CompoundPropertySchema)
    def patch(self, data, id):
        """Update compound property"""

        prop = record_exists(db, mdl.CompoundProperty, id)
        prop.update(data)
        db.session.commit()
        return prop.first()
