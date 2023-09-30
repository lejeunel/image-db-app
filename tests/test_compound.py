#!/usr/bin/env python3

new = {"name": "test_compound", "property_id": 8}


def test_update_wrong_id(client):
    item = client.get("compounds/").json[0]

    res = client.patch(
        "compounds/{}".format(item["id"] + "asdf"),
        json={"name": "updated_name"},
    )
    assert res == 404


def test_create_duplicate(client):
    dup = dict(new)
    dup["name"] = "compound_0"
    res = client.post("compounds/", json=dup)
    assert res == 424


def test_create(client):
    res = client.post("compounds/", json=new)
    assert res == 201


def test_update(client):
    cpd = client.get("compounds/").json[0]

    res = client.patch(
        "compounds/{}".format(cpd["id"]),
        json={"name": "updated_name"},
    )
    assert res == 200
    assert res.json["name"] == "updated_name"


def test_delete_used(client):
    cpd = client.get("compounds/").json[0]

    res = client.delete("compounds/{}".format(cpd["id"]))
    assert res == 424


def test_get(client):
    res = client.get("compounds/")
    assert res == 200


def test_delete_unused(client):
    res = client.post("compounds/", json=new)
    res = client.delete("compounds/{}".format(res.json["id"]))
    assert res == 204


def test_get_compound_properties(client):
    res = client.get("compounds/prop/")
    assert res == 200

def test_create_compound_properties_wrong_type(client):
    res = client.post(
        "compounds/prop/", json={"type": "wrong_type", "value": "the value"}
    )
    assert res == 422

def test_create_compound_properties_and_assign(client):
    prop = client.post(
        "compounds/prop/", json={"type": "target", "value": "a new target"}
    )
    assert prop == 201

    compound_id = client.get('compounds/').json[0]['id']
    res = client.patch(f"compounds/{compound_id}", json={'property_id': prop.json['id']})
    assert res.json['target'] == 'a new target'
