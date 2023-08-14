#!/usr/bin/env python

from ..models import Item
from flask import Blueprint, render_template, request, url_for, abort
import json2table
from flask.views import View
from ..schema import ItemsSchema

import numpy as np
import plotly
import plotly.express as px
import json

class ItemView(View):
    """
    View class that displays an image
    """

    def dispatch_request(self, id):
        """
        https://plotly.com/python/imshow/
        """

        q = get_images_with_meta()
        image = q.filter(Image.id == id).first()
        if image is None:
            abort(404)

        image_ = imstore.store.get_image(image.key)
        fig = px.imshow(image_, contrast_rescaling='minmax')
        fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
        fig.update_layout(width=800, height=800)
        fig.show()

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # strip some fields
        item = {k:v for k,v in image._asdict().items() if k not in ['section_id', 'timepoind_id']}
        item = append_tag_row(item)

        table = json2table.convert(
            item,
            build_direction="LEFT_TO_RIGHT",
            table_attributes={
                "style": "width:100%",
                "class": "table table-bordered",
            },
        )


        return render_template(
            "detail/image.html",
            table=table,
            graphJSON=graphJSON
        )
