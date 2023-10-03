from collections import OrderedDict

import json2table
from flask import url_for

from ..schemas.plate import PlateSchema
from ..schemas.section import SectionSchema
from . import GenericDetailedView


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
    # res_["stack"] = make_link_stack(section.stack)
    res_["cell"] = make_link_cell(section.cell)

    return res_


def make_plate_summary(plate):
    """
    Build summary of plate with links to sections
    """

    data = PlateSchema().dump(plate)
    data["sections"] = []
    for s in plate.sections:
        data["sections"] += [make_section_summary(s)]

    # sort by section range
    data["sections"] = sorted(data["sections"], key=lambda d: d["range"])
    return data


class DetailedPlateView(GenericDetailedView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def make_summary_table(self, plate):
        plate_summary = make_plate_summary(plate)
        plate_summary = {k:v for k,v in plate_summary.items() if k not in self.exclude_fields}
        table = json2table.convert(
            plate_summary,
            build_direction="LEFT_TO_RIGHT",
            table_attributes={
                "style": "width:100%",
                "class": "table table-bordered",
            },
        )

        return table
