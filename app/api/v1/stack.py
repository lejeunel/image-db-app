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
    url_prefix="/api/v1/stack",
    description="Ordered set of channels with matching rules",
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


def pivot_dict(data):
    """
    pivot association data to list of dicts
    """
    return [dict(zip(data, col)) for col in zip(*data.values())]


def check_num_params(data):
    """
    check that property values (regexp) and destinations (modalities)
    are of same length
    """
    n_elems = [len(v) for v in data.values()]
    if len(set(n_elems)) > 1:
        abort(424, message="Number of association parameter must match.")



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
    def patch(self, update_data, id):
        """Update stack"""
        res = Stack._update(id, update_data)

        return res

    @admin_required
    @blp.response(204)
    def delete(self, id):
        """Delete stack"""

        res = Stack._delete(id)

    @staticmethod
    def _create(data):

        data_assoc, data_stack = split_dict(data)

        check_num_params(data_assoc)
        check_duplicate(db.session, mdl.Stack, name=data["name"])

        # check that all modalities exist
        for m in data_assoc["modalities"]:
            record_exists(db, mdl.Modality, value=m, field="name")
        #
        # create stack record
        stack = mdl.Stack(**data_stack)
        db.session.add(stack)
        db.session.commit()

        # create associations
        assoc = []
        for r in pivot_dict(data_assoc):
            data = {
                "stack_id": stack.id,
                "modality_id": db.session.query(mdl.Modality).filter_by(name=r["modalities"])
                .first()
                .id,
                "chan": r["channels"],
            }
            assoc.append(mdl.StackModalityAssociation(**data))

        db.session.add_all(assoc)
        db.session.commit()

        return stack

    @staticmethod
    def _update(id, data):

        data_assoc, data_stack = split_dict(data)

        record_exists(db, mdl.Stack, id)

        if data_assoc:
            check_num_params(data_assoc)
            # check that all modalities exist
            for modality in data_assoc["modalities"]:
                record_exists(db,mdl.Modality, value=modality, field="name")

        q = db.session.query(mdl.Stack).filter_by(id=id)
        if data_stack:
            q.update(data_stack)
            db.session.commit()

        if data_assoc:
            # remove all associations
            assoc = db.session.query(mdl.StackModalityAssociation).filter_by(stack_id=id).all()
            for a in assoc:
                db.session.delete(a)
            db.session.commit()

            # add new associations
            for a in pivot_dict(data_assoc):
                modality_id = db.session.query(mdl.Modality).filter_by(name=a["modalities"]).first().id

                assoc = mdl.StackModalityAssociation(
                    stack_id=id, modality_id=modality_id, chan=a["channels"]
                )
                db.session.add(assoc)

        db.session.commit()

        return q.first()

    @staticmethod
    def _check_dependencies(id):

        # check if stack has dependencies
        stack = db.session.query(mdl.Stack).filter_by(id=id).first()
        if len(stack.sections) > 0:
            abort(
                424,
                message="Could not delete stack profile with id {}. Found parent section.".format(
                    id
                ),
            )

    @staticmethod
    def _can_delete(id):
        res = record_exists(db, mdl.Stack, id)
        Stack._check_dependencies(id)
        return res

    @staticmethod
    def _delete(id):

        res = Stack._can_delete(id).first()

        # delete associations
        assoc = db.session.query(mdl.StackModalityAssociation).filter_by(stack_id=id).all()
        for a in assoc:
            db.session.delete(a)

        db.session.delete(res)
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

        res = Stack._create(data)

        return res
