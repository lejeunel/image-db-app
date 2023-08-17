#!/usr/bin/env python3

import marshmallow as ma
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ... import db
from ...models import ItemTagAssociation, Tag
from . import (
    admin_required,
    check_dependencies,
    check_duplicate,
)
from app.utils import record_exists

blp = Blueprint(
    "Tag",
    "Tag",
    url_prefix="/api/v1/tag",
    description="Annotation tags",
)


class TagSchema(ma.Schema):
    class Meta:
        ordered = True

    id = ma.fields.UUID(dump_only=True)
    name = ma.fields.String()
    comment = ma.fields.String()


@blp.route("/<uuid:id>")
class TagAPI(MethodView):
    model = Tag

    @blp.response(200, TagSchema)
    def get(self, id):
        """Get tag"""

        res = record_exists(Tag, id)
        return res.first()

    @admin_required
    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def put(self, update_data, id):
        """Update tag"""
        res = TagAPI._update(id, update_data)

        return res

    @admin_required
    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def patch(self, update_data, id):
        """Patch compound"""
        res = TagAPI._update(id, update_data)

        return res

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete tag"""

        TagAPI._delete(id)

    @staticmethod
    def _create(data):

        check_duplicate(db.session, Tag, name=data["name"])

        tag = Tag(**data)

        db.session.add(tag)
        db.session.commit()
        return tag

    @staticmethod
    def _update(id, data):

        tag = Tag.query.filter_by(id=id)
        if tag.first() is None:
            abort(404, message="Tag with id {} not found.".format(id))

        tag.update(data)
        db.session.commit()
        return tag.first()

    @staticmethod
    def _check_dependencies(id):
        a = ItemTagAssociation.query.filter_by(tag_id=id)
        if a.count() > 0:
            d = Tag.query.filter_by(id=id).first()
            abort(
                424,
                message="Could not delete tag (id: {}, name: {}). Found tagged item.".format(
                    id, d.name
                ),
            )

    @staticmethod
    def _can_delete(id):
        res = record_exists(Tag, id)
        TagAPI._check_dependencies(id)
        return res.first()

    @staticmethod
    def _delete(id):

        res = TagAPI._can_delete(id)

        db.session.delete(res)
        db.session.commit()


@blp.route("/")
class TagsAPI(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self):
        """Get all tags"""

        item = Tag.query.all()
        return item

    @admin_required
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, data):
        """Add a new tag"""
        res = TagAPI._create(data)

        return res
