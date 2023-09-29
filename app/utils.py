#!/usr/bin/env python3
import mimetypes
import os
from flask_smorest import abort
import arrow

additional_file_types = {".md": "text/markdown"}


def datetimeformat(date_str):
    dt = arrow.get(date_str)
    return dt.humanize()


def file_type(key):
    file_info = os.path.splitext(key)
    file_extension = file_info[1]
    try:
        return mimetypes.types_map[file_extension]
    except KeyError:
        filetype = "Unknown"
        if file_info[0].startswith(".") and file_extension == "":
            filetype = "text"

        if file_extension in additional_file_types.keys():
            filetype = additional_file_types[file_extension]

        return filetype


def flatten_list_of_dict(list_):
    dict_ = {}
    for k in list_[0].keys():
        dict_[k] = [r[k] for r in list_]
    return dict_

def record_exists(db, model, value, field="id"):

    item = db.session.query(model).filter_by(**{field: value})
    if item.count() == 0:
        abort(
            404,
            message="Requested item of type {} with field/value {}/{} not found."
            .format(model.__name__, field, value),
        )
    return item
