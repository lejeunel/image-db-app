#!/usr/bin/env python3

import marshmallow as ma
from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_smorest import abort

from ... import db
from ... import models as mdl
from ... import schemas as sch
from .utils import admin_required, check_duplicate

blp = Blueprint(
    "Tag",
    "Tag",
    url_prefix="/api/v1/tags",
    description="Annotation tags",
)


@blp.route("/<uuid:id>")
class Tag(MethodView):
    model = mdl.Tag

    @blp.response(200, sch.TagSchema)
    def get(self, id):
        """Get tag"""

        return mdl.Tag.query.get_or_404(id)

    @admin_required
    @blp.arguments(sch.TagSchema)
    @blp.response(200, sch.TagSchema)
    def patch(self, data, id):
        """Update tag"""
        tag = mdl.Tag.query.get_or_404(id)

        tag.update(data)
        db.session.commit()
        return tag

        return res

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete tag"""

        tag = mdl.Tag.query.get_or_404(id)
        if len(tag.items) > 0:
            abort(
                424,
                message="Could not delete tag (id: {}, name: {}). Found tagged item.".format(
                    tag.id, tag.name
                ),
            )

        db.session.delete(tag)
        db.session.commit()

@blp.route("/")
class Tags(MethodView):
    @blp.response(200, sch.TagSchema(many=True))
    def get(self):
        """Get all tags"""

        return mdl.Tag.query.all()

    @admin_required
    @blp.arguments(sch.TagSchema)
    @blp.response(201, sch.TagSchema)
    def post(self, data):
        """Add a new tag"""
        check_duplicate(db.session, mdl.Tag, name=data["name"])

        tag = mdl.Tag(**data)

        db.session.add(tag)
        db.session.commit()
        return tag
