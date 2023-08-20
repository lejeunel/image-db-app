#!/usr/bin/env python3


new_modality = {
    "name": "test_modality",
    "target": "test_target",
    "comment": "test_comment",
}


def test_update(client):
    item = client.get("modality/").json[0]
    new_item = {'name': 'new name'}
    res = client.patch(
        "modality/{}".format(item["id"]),
        json=new_item,
    )
    assert res == 200
    assert res.json["name"] == "new name"



def test_delete_unused(client):
    res = client.post("modality/", json=new_modality)
    res = client.delete("modality/{}".format(res.json["id"]))
    assert res == 204


def test_delete_used(client):
    item = client.get("modality/").json[0]
    res = client.delete("modality/{}".format(item["id"]))
    assert res == 424


def test_get(client):
    res = client.get("modality/")
    assert res == 200


def test_create(client):
    res = client.post("modality/", json=new_modality)
    assert res == 201


def test_create_duplicate(client):
    dup_modality = dict(new_modality)
    dup_modality["name"] = "modality_0"
    res = client.post("modality/", json=dup_modality)
    assert res == 424
