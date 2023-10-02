#!/usr/bin/env python3
import pytest
from urllib.parse import urlencode
from app import models as mdl
from app import db

def test_bad_id(client):
    id = client.get("plates/").json[0]["id"]
    bad_id = str(id) + '0'
    res = client.get(f'plates/{bad_id}')
    assert res == 404

def test_create_existing(client):
    res = client.post("plates/", json={'name': 'first plate'})

    assert res == 424


def test_create(client):
    data = {"name": "new plate"}
    res = client.post("plates/", json=data)
    assert res == 201


def test_update(client):
    data = {'name': 'new name'}
    id = client.get("plates/").json[0]["id"]
    res = client.patch(f"plates/{id}", json=data)

    assert res == 200
    assert res.json["name"] == "new name"


def test_delete(client):
    plate_id = client.get("plates/").json[0]["id"]
    sections = client.get(f'plates/{plate_id}/sections').json

    client.delete(f"plates/{plate_id}")

    for s in sections:
        assert client.get(f"sections/{s['id']}") == 404

    plates = client.get("plates/").json
    timepoints = client.get("timepoints/").json
    items = client.get("items/").json

    assert len(plates) == len(items) == len(timepoints) == 0
