#!/usr/bin/env python3

new = {"name": "test_compound", "property_id": 8}


def test_update_wrong_id(client):
    item = client.get("compound/").json[0]

    res = client.put(
        "compound/{}".format(item["id"] + "asdf"),
        json={"name": "updated_name"},
    )
    assert res.status_code == 404


def test_create_duplicate(client):
    dup = dict(new)
    dup["name"] = "compound_0"
    res = client.post("compound/", json=dup)
    assert res.status_code == 424


def test_create(client):
    res = client.post("compound/", json=new)
    assert res.status_code == 201


def test_update(client):
    cpd = client.get("compound/").json[0]

    res = client.put(
        "compound/{}".format(cpd["id"]),
        json={"name": "updated_name"},
    )
    assert res.status_code == 200
    assert res.json["name"] == "updated_name"


def test_delete_used(client):
    cpd = client.get("compound/").json[0]

    res = client.delete("compound/{}".format(cpd["id"]))
    assert res.status_code == 424


def test_get(client):
    res = client.get("compound/")
    assert res.status_code == 200


def test_delete_unused(client):
    res = client.post("compound/", json=new)
    res = client.delete("compound/{}".format(res.json["id"]))
    assert res.status_code == 204

