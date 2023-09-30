from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db
from ... import models as mdl
from ... import schemas as sch
from .utils import admin_required, check_dependencies, check_duplicate

blp = Blueprint(
    "Compound", "Compound", url_prefix="/api/v1/compounds", description="Chemical compounds"
)


@blp.route("/<uuid:id>")
class Compound(MethodView):

    model = mdl.Compound

    @blp.response(200, sch.CompoundSchema)
    def get(self, id):
        """Get compound"""

        res = record_exists(db,self.model, id).first()
        return res

    @admin_required
    @blp.arguments(sch.CompoundSchema)
    @blp.response(200, sch.CompoundSchema)
    def patch(self, update_data, id):
        """Update compound"""
        res = self._update(id, update_data)

        return res


    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete compound"""

        res = self._delete(id)

    @staticmethod
    def _create(data):
        check_duplicate(db.session, mdl.Compound, name=data["name"])

        cpd = mdl.Compound(**data)

        db.session.add(cpd)
        db.session.commit()
        return cpd

    @staticmethod
    def _update(id, data):

        record_exists(db,mdl.Compound, id)

        cpd = mdl.Compound.query.filter_by(id=id)
        cpd.update(data)
        db.session.commit()
        return cpd.first()

    @staticmethod
    def _can_delete(id):
        record_exists(db,mdl.Compound, value=id, field="id")
        check_dependencies(mdl.Compound, value=id, field="id", remote="sections")

    @staticmethod
    def _delete(id):

        Compound._can_delete(id)

        cpd = mdl.Compound.query.filter_by(id=id).first()
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

        res = Compound._create(data)

        return res

@blp.route("/prop/")
class CompoundProperty(MethodView):
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
