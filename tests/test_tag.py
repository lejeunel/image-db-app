#!/usr/bin/env python3

new = {"name": "newtag", "comment": "A new tag."}

def test_delete_used(client):
    item = client.get("tags/").json[0]
    res = client.delete("tags/{}".format(item['id']))
    assert res == 424


def test_update(client):
    item = client.get("tags/").json[0]
    res = client.patch(
        "tags/{}".format(item['id']),
        json={"name": "updated_name"},
    )
    assert res == 200
    assert res.json['name'] == 'updated_name'


def test_create_duplicate(client):
    res = client.post(
        "tags/", json={'name': 'tag_1'}
    )
    assert res == 424


def test_create(client):
    res = client.post(
        "tags/", json=new
    )
    assert res == 201



def test_get(client):
    res = client.get("tags/")
    assert res == 200


def test_delete_unused(client):
    res = client.post(
        "tags/", json=new
    )
    res = client.delete("tags/{}".format(res.json["id"]))
    assert res == 204
