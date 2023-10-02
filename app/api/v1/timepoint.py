#!/usr/bin/env python3
#!/usr/bin/env python3

from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db, parser
from ... import models as mdl
from ... import schemas as sch
from .utils import admin_required, check_duplicate

blp = Blueprint(
    "TimePoint", "TimePoint", url_prefix="/api/v1/timepoints", description=""
)


@blp.route("/<uuid:id>")
class TimePoint(MethodView):
    model = mdl.TimePoint

    @blp.response(200, sch.TimePointSchema)
    def get(self, id):
        """Get timepoint"""

        return mdl.TimePoint.query.get_or_404(id)

    @admin_required
    @blp.arguments(sch.TimePointSchema)
    @blp.response(200, sch.TimePointSchema)
    def patch(self, data, id):
        """Update timepoint."""
        res = mdl.TimePoint.query.get_or_404(id)
        q.update(data)
        db.session.commit()

        return q.first()

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete timepoint"""

        timepoint = mdl.TimePoint.query.get_or_404(id)

        db.session.delete(timepoint)

        db.session.commit()


def create_timepoint(data):
    check_duplicate(db.session, mdl.TimePoint, uri=data["uri"])
    record_exists(db, mdl.Plate, data["plate_id"])

    timepoint = mdl.TimePoint(**data)
    db.session.add(timepoint)
    db.session.commit()

    items = parser(
        base_uri=timepoint.uri,
        plate_id=timepoint.plate_id,
        timepoint_id=timepoint.id,
    )
    db.session.add_all(items)

    return timepoint


@blp.route("/")
class TimePoints(MethodView):
    @blp.response(200, sch.TimePointSchema(many=True))
    def get(self):
        """Get all timepoints"""

        return mdl.TimePoint.query.all()
