#!/usr/bin/env python3
from app import ma
from marshmallow import post_dump
from ..models.stack import Stack


class StackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Stack
        additional = ('modalities', 'channels')

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("Stack.Stack", values=dict(id="<id>")),
            "collection": ma.URLFor("Stack.Stacks"),
        })

    @post_dump()
    def modalities_channels(self, data, **kwargs):
        data['modalities'] = [m.name for m in data['modalities']]
        data['channels'] = list(data['channels'])
        return data
