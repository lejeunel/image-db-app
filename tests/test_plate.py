#!/usr/bin/env python3
from marshmallow import ValidationError
from app.config import default as cfg
from app.models import TimePoint, ItemTagAssociation
from app import parser
from app.exceptions import ParsingException
from unittest.mock import patch


existing = {
    "name": "first plate",
    "timepoints": [{"uri": 'scheme://project/exp1/tp1/'}],
}

new = {
    "name": "new plate",
    "timepoints": [{"uri": 'scheme://project/exp3/tp1/'}],
}


def test_delete(client):


    plate_id = client.get("plate/").json[0]["id"]
    res = client.delete(f"plate/{plate_id}")

    plates = client.get("plate/").json
    items = client.get("items/").json

    assert len(plates) == len(items) == 0


def test_create_new_plate(client):
    res = client.post("plate/", json=new)
    assert res.status_code == 201


def test_create_duplicate_timepoint(client):

    data = dict(existing)
    data['name'] = 'new name'
    res = client.post("plate/", json=data)
    assert res.status_code == 424

def test_create_duplicate_plate(client):

    new = dict(existing)

    res = client.post("plate/", json=new)
    assert res.status_code == 424


def test_update(client):
    data = dict(existing)
    data["name"] = "new name"
    id = client.get('plate/').json[0]['id']
    res = client.put(f"plate/{id}", json=data)

    assert res.status_code == 200
    assert res.json["name"] == "new name"

def test_create_bad_uri(app, client):

    from app import db
    from .conftest import TestReader

    class FailingReader(TestReader):
        def __call__(self, *args, **kwargs):
            raise ParsingException(message='test')


    with app.app_context():
        reader = FailingReader()
        parser.init_app(app, db, reader)

        res = client.post("plate/", json=new)
        assert res.status_code == 400
