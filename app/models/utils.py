from marshmallow import ValidationError
from urllib.parse import urlparse


def _concat_properties(
        db, property_model, data, prefix="compound_", id_field="compound_property_id", **kwargs
):
    # get properties of all ancestors
    properties = (
        db.session.get(property_model, data[id_field])
        .path_to_root()
        .all()
    )
    properties = [(p.type._name_, p.value) for p in properties]

    # convert to dict and concatenate prefix
    properties = {prefix + f"{p[0]}": p[1] for p in properties}

    data = {**data, **properties}
    return data
