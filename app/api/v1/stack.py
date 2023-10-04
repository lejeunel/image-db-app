#!/usr/bin/env python3

from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ... import db
from ... import models as mdl
from ...schemas import StackSchema
from .utils import admin_required, check_duplicate

blp = Blueprint(
    "Stack",
    "Stack",
    url_prefix="/api/v1/stacks",
    description="Multiplexing profiles. Defines image modality to channel associations.",
)


def split_dict(data):
    """
    Split a dictionary into two dictionaries,
    where the first has items that contains list, and the second
    has all other items
    """

    out = dict()
    for k, v in data.items():
        if isinstance(v, list):
            out = {**out, **{k: v}}
    for k in out.keys():
        data.pop(k)

    return out, data

def reset_associations(stack_id, config):

    stack = mdl.Stack.query.get(stack_id)
    # check that all modalities exist
    for d in config:
        record_exists(db, mdl.Modality, value=d['modality_name'], field="name")

    # delete existing associations
    assocs = mdl.StackModalityAssociation.query.filter_by(stack_id = stack_id)
    assocs.delete()
    db.session.commit()

    # create associations
    assoc = []
    for d in config:
        data = {
            "stack_id": stack.id,
            "modality_id": mdl.Modality.query.filter_by(name=d["modality_name"])
            .first()
            .id,
            "chan": d["channel"],
        }
        assoc.append(mdl.StackModalityAssociation(**data))

    db.session.add_all(assoc)
    db.session.commit()


@blp.route("/<uuid:id>")
class Stack(MethodView):
    model = mdl.Stack

    @blp.response(200, StackSchema)
    def get(self, id):
        """Get stack"""

        stack = db.session.query(mdl.Stack).filter_by(id=id).first()
        if stack is None:
            abort(404, message="Not found.")
        return stack

    @admin_required
    @blp.arguments(StackSchema)
    @blp.response(200, StackSchema)
    def patch(self, data, id):
        """Update stack"""

        data_assoc, data_stack = split_dict(data)

        stack = mdl.Stack.query.get_or_404(id)
        if data_stack:
            stack.update(data_stack)
            db.session.commit()

        if data_assoc:
            reset_associations(id, data_assoc['config'])

        return stack

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete stack"""

        stack = mdl.Stack.query.get_or_404(id)
        if len(stack.plates) > 0:
            abort(
                424,
                message="Could not delete stack profile with id {}. Found parent plate.".format(
                    id
                ),
            )

        # delete associations
        assoc = db.session.query(mdl.StackModalityAssociation).filter_by(stack_id=id).all()
        for a in assoc:
            db.session.delete(a)

        db.session.delete(stack)
        db.session.commit()


@blp.route("/")
class Stacks(MethodView):
    @blp.response(200, StackSchema(many=True))
    def get(self):
        """Get all stacks"""

        item = mdl.Stack.query.all()
        return item

    @admin_required
    @blp.arguments(StackSchema)
    @blp.response(201, StackSchema)
    def post(self, data):
        """Add a new stack"""

        data_assoc, data_stack = split_dict(data)

        check_duplicate(db.session, mdl.Stack, name=data["name"])

        # create stack record
        stack = mdl.Stack(**data_stack)
        db.session.add(stack)
        db.session.commit()

        if data_assoc:
            reset_associations(stack.id, data_assoc['config'])

        return stack
