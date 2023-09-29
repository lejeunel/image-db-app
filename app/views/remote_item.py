#!/usr/bin/env python

import json
import mimetypes

import json2table
import numpy as np
import plotly
import plotly.express as px
from app.api.v1.items import get_items_with_meta
from flask import render_template
from flask.views import View

from ..schemas.item import ItemSchema
from ..reader.base import BaseReader


class RemoteItemView(View):
    """
    View class that displays a remote data item
    """

    def __init__(self, reader: BaseReader, items_per_page=20):
        self.reader = reader

    @staticmethod
    def image_to_json(image: np.ndarray, width=800, height=800):
        fig = px.imshow(image, contrast_rescaling='minmax')
        fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
        fig.update_layout(width=width, height=height)
        # fig.show()

        json_image = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return json_image

    @staticmethod
    def guess_type(uri: str) -> str:
        return mimetypes.guess_type(uri)[0].split('/')[0]


    def dispatch_request(self, id):
        """
        """

        from ..models.item import Item

        q = get_items_with_meta()
        item = q.filter(Item.id == id).first()
        meta_data = ItemSchema().dump(item)
        meta_table = json2table.convert(
            meta_data,
            build_direction="LEFT_TO_RIGHT",
            table_attributes={
                "style": "width:100%",
                "class": "table table-bordered",
            },
        )

        content = self.reader(item.uri)
        type_ = self.guess_type(item.uri)

        kwargs = {}
        if type_ == 'image':
            kwargs['graph_json'] = self.image_to_json(content)

        return render_template(
            "detail/item.html",
            table=meta_table,
            **kwargs
        )
