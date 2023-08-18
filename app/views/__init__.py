import json

import json2table
from flask import render_template, request
from flask.views import View
from app.api.v1.items import get_items_with_meta
from app import db
from app.models.item import ItemSchema


def make_item_pagination(items, page, items_per_page):
    # TODO this should use schema

    items_paginate = items.paginate(page=page, per_page=items_per_page, error_out=False)
    items = ItemSchema(many=True).dump(items_paginate)

    if items:
        # rename keys to only keep file name
        for im in items:
            im["uri"] = im["uri"].split("/")[-1]
    else:
        items = []

    return items_paginate, items


class GenericDetailedView(View):
    """
    Generic view class that displays details on a given object.

    base: Class that provides a get method to retrieve data as a dict
    template: path to template file
    """

    def __init__(self, model, schema, items_per_page):
        self.model = model
        self.schema = schema
        self.items_per_page = items_per_page
        self.template = "detail/generic.html"

    def infer_name(self, data):
        if "name" in data:
            return data["name"]
        return str(data["id"])

    def make_summary_table(self, obj):
        data = self.schema().dump(obj)
        table = json2table.convert(
            data,
            build_direction="LEFT_TO_RIGHT",
            table_attributes={
                "style": "width:100%",
                "class": "table table-bordered",
            },
        )

        return table

    @staticmethod
    def remove_sub_ids(data: list[dict]):
        """
        remove 'something_id' fields
        """
        return [{k: v for k, v in d.items() if "_id" not in k} for d in data]


    def dispatch_request(self, id):
        # build items meta data
        items = get_items_with_meta()
        items = items.filter(self.model.id == id)

        page = request.args.get("page", 1, type=int)

        items_paginate, items = make_item_pagination(
            items, page, self.items_per_page
        )

        items = self.remove_sub_ids(items)

        obj = db.session.get(self.model, id)
        data = self.schema().dump(obj)
        table = self.make_summary_table(obj)
        name = self.infer_name(data)


        return render_template(
            self.template,
            table=table,
            typename=self.model.__name__,
            pagination=items_paginate,
            name=name,
            items=items,
        )


class ListView(View):
    """
    Generic view class that displays a list of all objects of a given type.

    model: Class that provides a get method to retrieve data as a dict
    obj: Class of db object
    """

    def __init__(self, model, schema, n_per_page=30):
        self.n_per_page = n_per_page
        self.model = model
        self.schema = schema
        self.name = model.__name__
        self.template = "overview/generic.html"
        self.exclude_fields = ["timepoints"]

    @staticmethod
    def fill_missing(data: list[dict], value=None):
        fields = [[k for k in d] for d in data]
        fields = list(set([f_ for f in fields for f_ in f]))
        data = [{k: d.get(k, value) for k in fields} for d in data]

        return data

    def dispatch_request(self):
        if "page" in request.args.keys():
            page = int(request.args["page"])
        else:
            page = 1
        paginate = self.model.query.paginate(
            page=page, per_page=self.n_per_page, error_out=False
        )

        data = self.schema(many=True).dump(paginate.items)
        data = [
            {k: v for k, v in d.items() if k not in self.exclude_fields} for d in data
        ]
        data = self.fill_missing(data)

        return render_template(
            self.template,
            data=data,
            pagination=paginate,
            typename=self.name.lower(),
            fullname=self.name,
        )
