#!/usr/bin/env python3
import json

new = {
    "name": "stack_1",
    "comment": "",
    "config": [{'modality_name': 'modality_0', 'channel': 1},
               {'modality_name': 'modality_1', 'channel': 2},
              {'modality_name': 'modality_2', 'channel': 3} ]
}


def test_association_update(client):
    stack = client.get("stacks/").json[0]
    stack_id = stack['id']

    new_assoc = {'modality_name': 'modality_0', 'channel': 4}
    client.patch(
        "stacks/{}".format(stack_id),
        json={'config': new_assoc},
    )
    assert new_assoc in client.get(f'stacks/{stack_id}').json


def test_delete_used_should_fail(client):
    item = client.get("stacks/").json[0]
    res = client.delete("stacks/{}".format(item["id"]))
    assert res == 424


def test_delete_unused(client):
    res = client.post("stacks/", json=new)
    res = client.delete("stacks/{}".format(res.json["id"]))
    assert res == 204


def test_update(client):
    res = client.post("stacks/", json=new)

    item = client.get("stacks/").json[0]

    res = client.patch(
        "stacks/{}".format(item["id"]),
        json={"name": "updated_name"},
    )
    assert res == 200
    assert res.json["name"] == "updated_name"


def test_create(client):

    res = client.post("stacks/", json=new)
    assert res == 201


def test_create_duplicate_name_should_fail(client):

    dup = dict(new)
    dup["name"] = "stack_0"
    res = client.post("stacks/", json=dup)
    assert res == 424
