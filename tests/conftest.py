#!/usr/bin/env python3
import json

from urllib.parse import urlparse
import pytest
from app import create_app
from app.reader.base import BaseReader
from app.reader import ReaderException
from flask import testing
from werkzeug.datastructures import Headers
from datetime import datetime
from copy import copy
from urllib.parse import urlencode
from flask import Flask


class TestClient(testing.FlaskClient):
    """
    Testing client with appropriate entitlement.
    This will make all authorizations pass.
    """

    def open(self, *args, **kwargs):
        entitlement_headers = Headers(
            {"user-profile": json.dumps({"entitlements": {"my-project": ["admin"]}})}
        )
        headers = kwargs.pop("headers", Headers())
        headers.extend(entitlement_headers)
        kwargs["headers"] = headers
        return super().open(*args, **kwargs)


class TestReader(BaseReader):
    def __init__(self):
        self.items = [
            "scheme://project/" + exp + "/" + tp + "/" + f"file_{row}{col:02d}_w{chan}.tiff"
            for exp in ["exp1", "exp2", "exp3"]
            for tp in ["tp1", "tp2"]
            for row in ["A", "B", "C"]
            for col in range(12)
            for chan in range(1, 5)
        ]

    def __call__(self, uri):
        scheme = urlparse(uri).scheme
        if scheme != "scheme":
            raise ReaderException(
                message=f"Provided scheme {scheme} not supported",
                operation="list location",
            )

        if uri[-1] != "/":
            raise ReaderException(
                message="Provided URI must end with '/'", operation="list location"
            )

        return [item for item in self.items if uri in item]


@pytest.fixture()
def app():
    from app import db, restapi, loader, register_blueprints

    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object("app.config.test")
    with app.app_context():
        db.init_app(app)
        db.create_all()
        restapi.init_app(app)
        register_blueprints(restapi)
        loader.init_app(app, TestReader())

        yield app

        # clean up / reset resources here
        db.drop_all()


@pytest.fixture()
def client(app):
    with app.app_context():
        client = app.test_client()
        yield client


@pytest.fixture(autouse=True)
def populate_db(app, client):
    modalities = [
        {"name": n, "target": t, "comment": ""}
        for n, t in zip(
            [f"modality_{m}" for m in range(4)],
            [f"modality_target_{t}" for t in range(4)],
        )
    ]
    for d in modalities:
        res = client.post("/api/v1/modality/", json=d)

    compounds = [
        {"name": f"compound_{c}", "target": f"compound_target_{t}"}
        for c, t in zip(range(4), range(4))
    ]
    for c in compounds:
        res = client.post("/api/v1/compound/", json=c)

    cells = [
        {"name": f"cell_{n}", "code": f"cell_{c}"} for n, c in zip(range(4), range(4))
    ]
    for c in cells:
        res = client.post("/api/v1/cell/", json=c)

    tags = [{"name": f"tag_{t}"} for t in range(4)]
    for t in tags:
        res = client.post("/api/v1/tag/", json=t)

    stacks = [
        {
            "name": f"stack_{s}",
            "modalities": [m for m in modalities],
            "regexps": ["%w1%", "%w2%", "%w3%"],
        }
        for s, modalities in zip(
            range(2),
            [
                ["modality_1", "modality_2", "modality_3"],
                ["modality_1", "modality_2", "modality_4"],
            ],
        )
    ]
    for s in stacks:
        res = client.post("/api/v1/stack/", json=s)

    times = ["2011-11-04T00:05:23", "2011-11-05T00:05:23"]
    plates = [
        {
            "name": "first plate",
            "timepoints": [
                {
                    "uri": "scheme://project/exp1/tp1/",
                    "time": times[0],
                },
                {
                    "uri": "scheme://project/exp1/tp2/",
                    "time": times[1],
                },
            ],
        },
    ]
    for p in plates:
        res = client.post("/api/v1/plate/", json=p)

    plate_id = client.get("/api/v1/plate/").json[0]["id"]

    sections = []
    for p in plates:
        res = client.post("/api/v1/plate/", json=p)

    sections = []

    new_section = {
        "col_start": 1,
        "col_end": 9,
        "row_start": "A",
        "row_end": "B",
        "cell_code": "cell_0",
        "stack_name": "stack_0",
        "compound_name": "compound_0",
        "compound_concentration": 0.0,
    }
    sections.append(new_section)
    new_section = copy(new_section)
    new_section = {
        "col_start": 10,
        "col_end": 12,
        "row_start": "A",
        "row_end": "B",
        "cell_code": "cell_0",
        "stack_name": "stack_0",
        "compound_name": "compound_0",
        "compound_concentration": 1.0,
    }
    sections.append(new_section)

    res = client.post(f"/api/v1/plate/{plate_id}/sections/", json=sections[0])

    tp_ids = [tp["id"] for tp in client.get("/api/v1/plate/").json[0]["timepoints"]]

    params = urlencode({"section_id": res.json["id"], "timepoint_id": tp_ids[0]})
    url = "/api/v1/items/tag/{}?{}".format("tag_1", params)
    res = client.post(url)

    res = client.post(f"/api/v1/plate/{plate_id}/sections", json=sections[1])

    params = urlencode({"section_id": res.json["id"], "timepoint_id": tp_ids[1]})
    url = "/api/v1/items/tag/{}?{}".format("tag_2", params)
    res = client.post(url)
    url = "/api/v1/items/tag/{}?{}".format("tag_3", params)
    res = client.post(url)
