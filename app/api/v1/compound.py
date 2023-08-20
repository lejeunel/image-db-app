from app.models.compound import (Compound, CompoundProperty,
                                 CompoundPropertySchema, CompoundSchema)
from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db
from . import admin_required, check_dependencies, check_duplicate

blp = Blueprint(
    "Compound", "Compound", url_prefix="/api/v1/compound", description="Chemical compounds"
)


@blp.route("/<uuid:id>")
class CompoundAPI(MethodView):

    model = Compound

    @blp.response(200, CompoundSchema)
    def get(self, id):
        """Get compound"""

        res = record_exists(db,self.model, id).first()
        return res

    @admin_required
    @blp.arguments(CompoundSchema)
    @blp.response(200, CompoundSchema)
    def patch(self, update_data, id):
        """Update compound"""
        res = CompoundAPI._update(id, update_data)

        return res


    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete compound"""

        res = CompoundAPI._delete(id)

    @staticmethod
    def _create(data):
        check_duplicate(db.session, Compound, name=data["name"])

        cpd = Compound(**data)

        db.session.add(cpd)
        db.session.commit()
        return cpd

    @staticmethod
    def _update(id, data):

        record_exists(db,Compound, id)

        cpd = Compound.query.filter_by(id=id)
        cpd.update(data)
        db.session.commit()
        return cpd.first()

    @staticmethod
    def _can_delete(id):
        record_exists(db,Compound, value=id, field="id")
        check_dependencies(Compound, value=id, field="id", remote="sections")

    @staticmethod
    def _delete(id):

        CompoundAPI._can_delete(id)

        cpd = Compound.query.filter_by(id=id).first()
        db.session.delete(cpd)
        db.session.commit()


@blp.route("/")
class CompoundsAPI(MethodView):
    model = Compound

    @blp.response(200, CompoundSchema(many=True))
    def get(self):
        """Get all compounds"""

        return Compound.query.all()

    @admin_required
    @blp.arguments(CompoundSchema)
    @blp.response(201, CompoundSchema)
    def post(self, data):
        """Add a new compound"""

        res = CompoundAPI._create(data)

        return res

@blp.route("/prop/")
class CompoundPropertyAPI(MethodView):
    model = CompoundProperty

    @blp.response(200, CompoundPropertySchema(many=True))
    def get(self):
        """Get all compound properties"""

        return CompoundProperty.query.all()

    @admin_required
    @blp.arguments(CompoundPropertySchema)
    @blp.response(201, CompoundPropertySchema)
    def post(self, data):
        """Add a new compound property"""

        prop = CompoundProperty(**data)
        db.session.add(prop)
        db.session.commit()


        return prop
