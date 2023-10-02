from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db
from ... import models as mdl
from ... import schemas as sch
from .utils import admin_required, check_dependencies, check_duplicate

blp = Blueprint(
    "Compound",
    "Compound",
    url_prefix="/api/v1/compounds",
    description="Chemical compounds",
)


@blp.route("/<uuid:id>")
class Compound(MethodView):
    model = mdl.Compound

    @blp.response(200, sch.CompoundSchema)
    def get(self, id):
        """Get compound"""

        return mdl.Compound.query.get_or_404(id)

    @admin_required
    @blp.arguments(sch.CompoundSchema)
    @blp.response(200, sch.CompoundSchema)
    def patch(self, data, id):
        """Update compound"""
        cpd = mdl.Compound.query.get_or_404(id)
        cpd.update(data)

        return cpd

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete compound"""

        cpd = mdl.Compound.query.get_or_404(id)
        check_dependencies(mdl.Compound, value=id, field="id", remote="sections")

        db.session.delete(cpd)
        db.session.commit()


@blp.route("/")
class Compounds(MethodView):
    model = mdl.Compound

    @blp.response(200, sch.CompoundSchema(many=True))
    def get(self):
        """Get all compounds"""

        return mdl.Compound.query.all()

    @admin_required
    @blp.arguments(sch.CompoundSchema)
    @blp.response(201, sch.CompoundSchema)
    def post(self, data):
        """Add a new compound"""

        check_duplicate(db.session, mdl.Compound, name=data["name"])

        cpd = mdl.Compound(**data)

        db.session.add(cpd)
        db.session.commit()
        return cpd
