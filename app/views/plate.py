#!/usr/bin/env python3


from collections import OrderedDict

import json2table
from flask import Blueprint, render_template, request, url_for
from flask.views import View

from ..schema import PlateSchema, SectionSchema
from ..models import Plate, TimePoint
from . import make_image_pagination
from . import ItemView


def make_link_compound(cpd):
    return "<a href={}>{}</a>".format(url_for("compound_detail", id=cpd.id), cpd.name)


def make_link_stack(stack):
    return "<a href={}>{}</a>".format(url_for("stack_detail", id=stack.id), stack.name)


def make_link_tags(tags):
    return ", ".join(
        [
            "<a href={}>{}</a>".format(url_for("tag_detail", id=t.id), t.name)
            for t in tags
        ]
    )


def make_link_cell(cell):
    return "<a href={}>{}</a>".format(url_for("cell_detail", id=cell.id), cell.name)


def make_link_section(section):
    return "<a href={}>{}</a>".format(
        url_for("section_detail", id=section.id), section.id
    )


def make_section_summary(section):
    """
    Build summary of section with links to stacks, cells, compounds, and tags
    """
    res = SectionSchema().dump(section)
    # res.pop("id")
    res_ = OrderedDict()
    res_["id"] = make_link_section(section)
    res_["range"] = "[({},{}), ({},{})]".format(
        res["row_start"], res["row_end"], res["col_start"], res["col_end"]
    )
    res_["compound"] = make_link_compound(section.compound)
    res_["compound_concentration"] = section.compound_concentration
    res_["stack"] = make_link_stack(section.stack)
    res_["cell"] = make_link_cell(section.cell)

    return res_


def make_plate_summary(plate):
    """
    Build summary of plate with links to stacks
    """

    res = PlateSchema().dump(plate)
    res["sections"] = []
    for s in plate.sections:
        res["sections"] += [make_section_summary(s)]
    # sort by section range
    res["sections"] = sorted(res["sections"], key=lambda d: d["range"])
    return res


class PlateView(ItemView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def make_summary_table(self, id):
        plate = self.model.query.get(id)
        plate_summary = make_plate_summary(plate)
        table = json2table.convert(
            plate_summary,
            build_direction="LEFT_TO_RIGHT",
            table_attributes={
                "style": "width:100%",
                "class": "table table-bordered",
            },
        )

        return table
