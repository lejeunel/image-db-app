#!/usr/bin/env python3
#!/usr/bin/env python3

from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint

from ... import db, parser
from ...models.timepoint import TimePoint, TimePointSchema
from ...models.plate import Plate
from ...models.item import ItemTagAssociation

from . import admin_required, check_duplicate

blp = Blueprint(
    "TimePoint", "TimePoint", url_prefix="/api/v1/timepoint", description=""
)


@blp.route("/<uuid:id>")
class TimePointAPI(MethodView):
    model = TimePoint

    @blp.response(200, TimePointSchema)
    def get(self, id):
        """Get plate"""

        res = record_exists(db, TimePoint, id)

        return res.first()

    @admin_required
    @blp.arguments(TimePointSchema)
    @blp.response(200, TimePointSchema)
    def patch(self, data, id):
        """Update timepoint."""
        q = record_exists(db, TimePoint, id)
        q.update(data)
        db.session.commit()

        return q.first()

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete timepoint"""

        timepoint = record_exists(db, TimePoint, id)

        db.session.delete(timepoint.first())

        db.session.commit()


@blp.route("/")
class TimePointsAPI(MethodView):

    @blp.response(200, TimePointSchema(many=True))
    def get(self):
        """Get all timepoints"""

        return TimePoint.query.all()

    @admin_required
    @blp.arguments(TimePointSchema)
    @blp.response(201, TimePointSchema)
    def post(self, data):
        """Add a new timepoint"""

        check_duplicate(db.session, TimePoint, uri=data["uri"])
        record_exists(db, Plate, data["plate_id"])

        timepoint = TimePoint(**data)
        db.session.add(timepoint)
        db.session.commit()

        items = parser(
            base_uri=timepoint.uri,
            plate_id=timepoint.plate_id,
            timepoint_id=timepoint.id,
        )
        db.session.add_all(items)

        return timepoint

