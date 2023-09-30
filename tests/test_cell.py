#!/usr/bin/env python3

new = {"name": "test_cell", "code": "test_code"}


def test_update(client):
    cell = client.get("cells/").json[0]

    res = client.patch(
        "cells/{}".format(cell["id"]),
        json={"name": "updated_name"},
    )
    assert res == 200
    assert res.json["name"] == "updated_name"


def test_update_wrong_id(client):
    cell = client.get("cells/").json[0]

    res = client.patch(
        "cell/{}".format(cell["id"] + "asdf"),
        json={"name": "updated_name"},
    )
    assert res == 404


def test_delete_used(client):
    cell = client.get("cells/").json[0]

    res = client.delete("cells/{}".format(cell["id"]))
    assert res == 424


def test_create_duplicate(client):
    dup = dict(new)
    dup["code"] = "cell_code_0"
    res = client.post("cells/", json=dup)
    assert res == 424


def test_create(client):
    res = client.post("cells/", json=new)
    assert res == 201
    assert res.json["name"] == "test_cell"


def test_get(client):
    res = client.get("cells/")
    assert res == 200


def test_delete_unused(client):
    res = client.post("cells/", json=new)
    res = client.delete("cells/{}".format(res.json["id"]))
    assert res == 204
