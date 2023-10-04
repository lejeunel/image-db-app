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

        if 'parent_id' in data:
            mdl.CompoundProperty.query.get_or_404(data['parent_id'])

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

        return mdl.CompoundProperty.query.get_or_404(id)

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete compound property"""
        res = mdl.CompoundProperty.query.get_or_404(id)
        db.session.delete(res)

    @admin_required
    @blp.arguments(sch.CompoundPropertySchema)
    @blp.response(200, sch.CompoundPropertySchema)
    def patch(self, data, id):
        """Update compound property"""

        prop =  mdl.CompoundProperty.query.get_or_404(id)
        prop.update(data)
        db.session.commit()
        return prop
