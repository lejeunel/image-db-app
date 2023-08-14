#!/usr/bin/env python3
from app.config import default as cfg
from app.models import TimePoint

existing = {
    "name": "first plate",
    "timepoints": [{"uri": 'scheme://store/exp1/tp1/'}],
}

new = {
    "name": "new plate",
    "timepoints": [{"uri": 'scheme://store/exp3/tp1/'}],
}


def test_delete(client):
    plate_id = client.get("/api/plate/").json[0]["id"]
    res = client.delete(f"/api/plate/{plate_id}")

    plates = client.get("/api/plate/").json
    items = client.get("/api/items/").json

    assert len(plates) == len(items) == 0


def test_create_new_plate(client):
    res = client.post("/api/plate/", json=new)
    assert res.status_code == 201


def test_create_duplicate_timepoint(client):

    store = DummyStore()
    plates = client.get("/api/plate/").json

    new = plates[0]
    new["name"] = "third plate"
    timepoint = {'uri': new['timepoints'][0]['uri']}
    new["timepoints"] = [timepoint]
    new.pop('id')
    res = client.post("/api/plate/", json=new)
    assert res.status_code == 424

def test_create_duplicate_name(client):

    new = dict(existing)

    res = client.post("/api/plate/", json=new)
    assert res.status_code == 424


def test_update(client):
    new = dict(existing)
    new["name"] = "third plate"
    new["timepoints"][0]["uri"] = str(store.buckets[2]) + "/" + "TimePoint3"
    res = client.post("/api/plate/", json=new)

    updated_plate = dict(new)
    updated_plate["name"] = "updated name"
    res = client.put(
        "/api/plate/{}".format(res.json["id"]),
        json={"name": "updated_name"},
    )

    assert res.status_code == 200
    assert res.json["name"] == "updated_name"
