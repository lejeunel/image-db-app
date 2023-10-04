import json

import json2table
from flask import render_template, request
from flask.views import View


def infer_columns(data: list[dict]):
    """
    infer from a set of records the "fields", i.e.
    the set of dictionary keys of records without missing values
    """

    data_ = sorted(data, key=lambda d: len(d))
    return data_[-1].keys()


def make_item_pagination(items, page, items_per_page):
    from app.schemas.item import ItemSchema

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

    def __init__(self, model, schema, items_per_page=20):
        self.model = model
        self.schema = schema
        self.items_per_page = items_per_page
        self.template = "detail/generic.html"
        self.exclude_fields = ["_links"]

    def infer_name(self, data):
        if "name" in data:
            return data["name"]
        return str(data["id"])

    def make_summary_table(self, obj):
        data = self.schema().dump(obj)
        data = {k: v for k, v in data.items() if k not in self.exclude_fields}
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
        from app.api.v1.item import get_items_with_meta
        from app import db

        items = get_items_with_meta()
        items = items.filter(self.model.id == id)

        page = request.args.get("page", 1, type=int)

        items_paginate, items = make_item_pagination(items, page, self.items_per_page)

        items = self.remove_sub_ids(items)
        items = [
            {k: v for k, v in item.items() if k not in self.exclude_fields}
            for item in items
        ]

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
        self.exclude_fields = ["timepoints", "property_id", "_links"]

    def make_paginated_data(self):
        if "page" in request.args.keys():
            page = int(request.args["page"])
        else:
            page = 1
        paginate = self.model.query.paginate(
            page=page, per_page=self.n_per_page, error_out=False
        )

        data = self.schema(many=True).dump(paginate.items)
        return data, paginate

    def make_columns(self, data):
        columns = infer_columns(data)
        columns = [c for c in columns if c not in self.exclude_fields]
        return columns

    def dispatch_request(self):
        data, paginate = self.make_paginated_data()

        columns = self.make_columns(data)

        return render_template(
            self.template,
            data=data,
            columns=columns,
            pagination=paginate,
            typename=self.name.lower(),
            fullname=self.name,
        )


def register_views(app, reader=None):
    from .index import bp as main_bp

    with app.app_context():
        from .remote_item import RemoteItemView

        from .. import models as mdl
        from .. import schemas as sch
        from . import GenericDetailedView, ListView
        from .plate import DetailedPlateView
        from .stack import StackView
        from .compound import CompoundView

        app.register_blueprint(main_bp, url_prefix="/")

        # Add detailed views
        for model, schema in zip(
            [
                mdl.Modality,
                mdl.Cell,
                mdl.Compound,
                mdl.Tag,
                mdl.Section,
            ],
            [
                sch.ModalitySchema,
                sch.CellSchema,
                sch.CompoundSchema,
                sch.TagSchema,
                sch.SectionSchema,
            ],
        ):
            name = model.__name__.lower()
            app.add_url_rule(
                f"/{name}/detail/<uuid:id>",
                view_func=GenericDetailedView.as_view(
                    f"{name}_detail", model, schema, app.config["VIEWS_ITEMS_PER_PAGE"]
                ),
            )

        app.add_url_rule(
            f"/plate/detail/<uuid:id>",
            view_func=DetailedPlateView.as_view(
                f"plate_detail",
                mdl.Plate,
                sch.PlateSchema,
                app.config["VIEWS_ITEMS_PER_PAGE"],
            ),
        )
        app.add_url_rule(
            f"/stack/detail/<uuid:id>",
            view_func=StackView.as_view(
                f"stack_detail",
                mdl.Stack,
                sch.StackSchema,
                app.config["VIEWS_ITEMS_PER_PAGE"],
            ),
        )

        # Add basic elements views
        for obj, schema in zip(
            [mdl.Modality, mdl.Cell, mdl.Plate, mdl.Stack, mdl.Tag],
            [
                sch.ModalitySchema,
                sch.CellSchema,
                sch.PlateSchema,
                sch.StackSchema,
                sch.TagSchema,
            ],
        ):
            name = obj.__name__.lower()
            app.add_url_rule(
                f"/{name}/list/".lower(),
                view_func=ListView.as_view(
                    f"{name}_list", obj, schema, app.config["VIEWS_ITEMS_PER_PAGE"]
                ),
            )

        app.add_url_rule(
            "/item/<uuid:id>",
            view_func=RemoteItemView.as_view(
                "item", reader, app.config["VIEWS_ITEMS_PER_PAGE"]
            ),
        )

        app.add_url_rule(
            "/compound/list/",
            view_func=CompoundView.as_view(
                f"compound_list",
                mdl.Compound,
                sch.CompoundSchema,
                app.config["VIEWS_ITEMS_PER_PAGE"],
            ),
        )
