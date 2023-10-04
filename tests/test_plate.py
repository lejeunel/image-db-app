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


def test_delete_should_also_delete_subresources(client):
    plate_id = client.get("plates/").json[0]["id"]

    client.delete(f"plates/{plate_id}")

    plates = client.get("plates/").json
    timepoints = client.get("timepoints/").json
    sections = client.get(f'sections/').json
    items = client.get("items/").json

    assert len(plates) == len(items) == len(timepoints) == len(sections) == 0

def test_delete_should_conserve_stacks_tags_compounds(client):
    plate_id = client.get("plates/").json[0]["id"]

    client.delete(f"plates/{plate_id}")

    stacks = client.get("stacks/").json
    tags = client.get("tags/").json
    compounds = client.get("compounds/").json
    props = client.get("compound-properties/").json

    assert len(stacks) > 0
    assert len(tags) > 0
    assert len(compounds) > 0
    assert len(props) > 0

def test_get_timepoints(client):
    res = client.get('plates/')
    res = client.get(res.json[0]['_links']['timepoints'])
    assert res == 200

def test_get_sections(client):
    res = client.get('plates/')
    res = client.get(res.json[0]['_links']['sections'])
    assert res == 200

def test_get_stack(client):
    res = client.get('plates/')
    res = client.get(res.json[0]['_links']['stack'])
    assert res == 200
