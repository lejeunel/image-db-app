#!/usr/bin/env python3
import pprint

from app.models.compound import CompoundProperty
from flask import render_template

from . import ListView

def cat_to_json(item):
    return {"id": item.id, "type": item.type.name, "value": item.value}


def make_properties():
    roots = CompoundProperty.query.filter_by(parent_id=None)

    props = [p.drilldown_tree(json=True, json_fields=cat_to_json)[0] for p in roots]

    return props

def clean_tree(tree:list[dict], field_to_clean='label'):

    tree.pop(field_to_clean)
    if 'children' in tree:
        tree['children'] = [clean_tree(c, field_to_clean) for c in tree['children']]

    return tree



class CompoundView(ListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = "overview/compounds.html"

    def dispatch_request(self):
        data, paginate = self.make_paginated_data()
        columns = self.make_columns(data)

        props = make_properties()

        props = [clean_tree(p) for p in props]
        return render_template(
            self.template,
            data=data,
            columns=columns,
            pagination=paginate,
            typename=self.name.lower(),
            fullname=self.name,
            json_compound_properties=props,
        )
