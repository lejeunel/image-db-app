#!/usr/bin/env python3
import json

new = {
    "name": "stack_1",
    "comment": "",
    "modalities": ["modality_0", "modality_1", "modality_2"],
    "channels": [1, 2, 3],
}


def test_association_update(client):
    res = client.post("stack/", json=new)
    all = client.get("stack/")
    item = json.loads([s for s in all.response][0])[0]

    update_assoc = dict(new)

    update_assoc["modalities"] = ["BrightField", "WGA"]
    update_assoc["chan"] = [2, 4]
    res = client.put(
        "stack/{}".format(item["id"]),
        json={"name": "updated_name"},
    )
    assert res.status_code == 200


def test_delete_used(client):
    item = client.get("stack/").json[0]
    res = client.delete("stack/{}".format(item["id"]))
    assert res.status_code == 424


def test_delete_unused(client):
    res = client.post("stack/", json=new)
    res = client.delete("stack/{}".format(res.json["id"]))
    assert res.status_code == 204


def test_update(client):
    res = client.post("stack/", json=new)

    item = client.get("stack/").json[0]

    res = client.put(
        "stack/{}".format(item["id"]),
        json={"name": "updated_name"},
    )
    assert res.status_code == 200
    assert res.json["name"] == "updated_name"

def test_add_channel(client):
    res = client.post("stack/", json=new)

    item = client.get("stack/").json[0]

    res = client.put(
        "stack/{}".format(item["id"]),
        json={"modalities": ["modality_0", "modality_1", "modality_2", "modality_3"],
              "channels": [1, 2, 3, 4]}
    )
    assert res.status_code == 200


def test_create(client):

    res = client.post("stack/", json=new)
    assert res.status_code == 201


def test_create_duplicate(client):

    dup = dict(new)
    dup["name"] = "stack_0"
    res = client.post("stack/", json=dup)
    assert res.status_code == 424
