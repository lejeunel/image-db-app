import json

import json2table
from flask import render_template, request
from flask.views import View
from app.utils import make_records
from app.schema import ImagesSchema


def make_image_pagination(images, page, images_per_page):

    images_paginate = images.paginate(
        page=page, per_page=images_per_page, error_out=False
    )
    images = [dict(im._mapping) for im in images_paginate.items]

    if images:

        # rename keys to only keep file name
        for im in images:
            im["key"] = im["key"].split("/")[-1]
        # we skip some fields
        col_names = [
            c
            for c in images[0].keys()
            if c not in ["id", "plate_id", "section_id", "stack", "cell", "cell_code"]
        ]
    else:
        images = []
        col_names = []

    return images_paginate, col_names, images


class ItemView(View):
    """
    Generic view class that displays details on a given object.

    base: Class that provides a get method to retrieve data as a dict
    template: path to template file
    """

    def __init__(self, model, schema, images_per_page):
        self.model = model
        self.schema = schema
        self.images_per_page = images_per_page
        self.template = "detail/generic.html"

    def get_item_name(self, id):
        if "name" in self.model.__mapper__.attrs:
            return self.model.query.get(id).name
        return str(id)

    def make_summary_table(self, id):
        item = self.model.query.get(id)
        item = json.loads(self.schema().dumps(item))
        table = json2table.convert(
            item,
            build_direction="LEFT_TO_RIGHT",
            table_attributes={
                "style": "width:100%",
                "class": "table table-bordered",
            },
        )

        return table

    def dispatch_request(self, id):
        from ..api.images import get_images_with_meta, append_tag_col

        # build image meta data
        images = get_images_with_meta()
        images = images.filter(self.model.id == id)

        page = request.args.get("page", 1, type=int)

        images_paginate, col_names, images = make_image_pagination(
            images, page, self.images_per_page
        )
        images = append_tag_col(images)

        table = self.make_summary_table(id)
        name = self.get_item_name(id)

        return render_template(
            self.template,
            table=table,
            typename=self.model.__name__,
            pagination=images_paginate,
            images_col_names=col_names + ["tags"],
            name=name,
            images=images,
        )


class ListView(View):
    """
    Generic view class that displays a list of all objects.

    base: Class that provides a get method to retrieve data as a dict
    obj: Class of db object
    template: path to template file
    """

    def __init__(self, model, n_per_page=30):
        self.n_per_page = n_per_page
        self.model = model
        self.name = model.__name__
        self.template = "overview/generic.html"
        self.curate_fields = [
            "_sa_instance_state",
            "sections",
            "well_row_col_regexp",
            "site_regexp",
            "ignore_regexp",
            "valid_regexp",
        ]

    def dispatch_request(self):
        if "page" in request.args.keys():
            page = int(request.args["page"])
        else:
            page = 1
        paginate = self.model.query.paginate(
            page=page, per_page=self.n_per_page, error_out=False
        )

        columns = self.model.__table__.columns.keys()
        columns = [c for c in columns if c not in self.curate_fields]
        data = [
            {k: v for k, v in d.__dict__.items() if k not in self.curate_fields}
            for d in paginate.items
        ]

        return render_template(
            self.template,
            columns=columns,
            data=data,
            pagination=paginate,
            typename=self.name.lower(),
            fullname=self.name,
        )
