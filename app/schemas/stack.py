#!/usr/bin/env python3
from app import ma, db
from marshmallow import post_dump, pre_dump, pre_load, post_load
from ..models.stack import Stack
from ..models.modality import Modality
from app.utils import record_exists

class StackAssoc(ma.Schema):
    modality_name = ma.String()
    channel = ma.Int()

class StackSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Stack

    id = ma.auto_field()
    name = ma.auto_field()
    comment = ma.auto_field()
    config = ma.List(ma.Nested(StackAssoc))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("Stack.Stack", values=dict(id="<id>")),
            "collection": ma.URLFor("Stack.Stacks"),
        })


    @post_dump()
    def write_assoc_config(self, data, **kwargs):
        stack = Stack.query.get(data['id'])
        data['config'] = [{'modality_name': m.name, 'channel': c}
                          for m,c in zip(stack.modalities, stack.channels)]
        return data
