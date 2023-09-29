#!/usr/bin/env python3
import pytest
from urllib.parse import urlencode

def test_create_existing(client):
    res = client.post("plate/", json={'name': 'first plate'})

    assert res == 424


def test_create(client):
    data = {"name": "new plate"}
    res = client.post("plate/", json=data)
    assert res == 201


def test_update(client):
    data = {'name': 'new name'}
    id = client.get("plate/").json[0]["id"]
    res = client.patch(f"plate/{id}", json=data)

    assert res == 200
    assert res.json["name"] == "new name"


def test_delete(client):
    plate_id = client.get("plate/").json[0]["id"]
    client.delete(f"plate/{plate_id}")

    plates = client.get("plate/").json
    timepoints = client.get("timepoint/").json
    items = client.get("items/").json

    assert len(plates) == len(items) == len(timepoints) == 0
