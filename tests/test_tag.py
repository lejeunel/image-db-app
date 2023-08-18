#!/usr/bin/env python3

new = {"name": "newtag", "comment": "A new tag."}

def test_delete_used(client):
    item = client.get("tag/").json[0]
    res = client.delete("tag/{}".format(item['id']))
    assert res == 424


def test_update(client):
    item = client.get("tag/").json[0]
    res = client.put(
        "tag/{}".format(item['id']),
        json={"name": "updated_name"},
    )
    assert res == 200
    assert res.json['name'] == 'updated_name'


def test_create_duplicate(client):
    res = client.post(
        "tag/", json={'name': 'tag_1'}
    )
    assert res == 424


def test_create(client):
    res = client.post(
        "tag/", json=new
    )
    assert res == 201



def test_get(client):
    res = client.get("tag/")
    assert res == 200


def test_delete_unused(client):
    res = client.post(
        "tag/", json=new
    )
    res = client.delete("tag/{}".format(res.json["id"]))
    assert res == 204
