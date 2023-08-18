#!/usr/bin/env python3
import json2table
from flask import url_for

from ..models.stack import Stack, StackSchema
from . import GenericDetailedView


def make_stack_summary(stack):
    """
    Build summary of stack with links to modalities
    """

    res = StackSchema().dump(stack)
    res.pop("modalities")
    res.pop("regexps")
    modality_links = []
    modality_labels = []
    for modality in stack.modalities:
        modality_links.append(url_for("modality_detail", id=modality.id))
        modality_labels.append(modality.name)
    res["modalities [name (pattern)]"] = [
        "<a href={}>{} ({})</a>".format(link, label, regexp)
        for link, label, regexp in zip(modality_links, modality_labels, stack.regexps)
    ]
    return res


class StackView(GenericDetailedView):
    """
    View class that displays details of a Stack.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def make_summary_table(self, id):
        stack = Stack.query.filter_by(id=id).first()
        stack_summary = make_stack_summary(stack)
        table = json2table.convert(
            stack_summary,
            build_direction="LEFT_TO_RIGHT",
            table_attributes={
                "style": "width:100%",
                "class": "table table-bordered",
            },
        )

        return table
