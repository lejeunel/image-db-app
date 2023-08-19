#!/usr/bin/env python3
import pytest

existing = {
    "name": "first plate",
    "timepoints": [{"uri": "scheme://project/exp1/tp1/"}],
}


@pytest.mark.parametrize(
    "name,base_uri,expected_status",
    [
        ("first plate", "scheme://project/exp3/tp1/", 424),
        ("new plate", "scheme://project/exp1/tp1/", 424),
        ("new plate", "badscheme://project/exp1/tp1/", 422),
        ("new plate", "scheme://project/exp1/tp1", 422),
    ],
)
def test_create_bad_inputs(client, name, base_uri, expected_status):
    data = {"name": name, "timepoints": [{"uri": base_uri}]}
    res = client.post("plate/", json=data)
    assert res == expected_status


def test_create_good_inputs(client):
    data = {"name": "new plate", "timepoints": [{"uri": "scheme://project/exp3/tp1/"}]}
    res = client.post("plate/", json=data)
    assert res == 201


def test_update(client):
    data = dict(existing)
    data["name"] = "new name"
    id = client.get("plate/").json[0]["id"]
    res = client.put(f"plate/{id}", json=data)

    assert res == 200
    assert res.json["name"] == "new name"


def test_delete(client):
    plate_id = client.get("plate/").json[0]["id"]
    res = client.delete(f"plate/{plate_id}")

    plates = client.get("plate/").json
    items = client.get("items/").json

    assert len(plates) == len(items) == 0
