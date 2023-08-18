#!/usr/bin/env python3


def test_update_section(client):
    plate_id = client.get("plate/").json[0]['id']
    section = client.get(f"plate/{plate_id}/sections").json[0]
    id = section["id"]

    res = client.put(
        f"section/{id}", json={"compound_name": "compound_0"}
    )
    assert res == 200
    assert res.json["compound_name"] == "compound_0"



def test_update_wrong_id(client):
    plate_id = client.get("plate/").json[0]['id']
    item = client.get(f"plate/{plate_id}/sections").json[0]

    res = client.put(
        "section/{}".format(item["id"] + "asdf"),
        json={"compound_name": "Tebuconazole"},
    )
    assert res == 404


def test_create_section(client):
    """
    Add section in available row
    """
    plate_id = client.get("plate/").json[0]['id']
    section = client.get(f'plate/{plate_id}/sections').json[0]
    section["row_start"] = "F"
    section["row_end"] = "F"
    section.pop('id')

    res = client.post(f"plate/{plate_id}/sections", json=section)
    assert res == 201


def test_create_overlap(client):
    """
    Add section that overlaps existing section
    """

    plate_id = client.get("plate/").json[0]['id']
    section = client.get(f'plate/{plate_id}/sections').json[0]
    section["row_start"] = "A"
    section["row_end"] = "A"
    section.pop('id')

    res = client.post(f"plate/{plate_id}/sections", json=section)
    assert res == 409


def test_create_out_range(client):
    """
    Add section out of bounds
    """

    plate_id = client.get("plate/").json[0]['id']
    section = client.get(f'plate/{plate_id}/sections').json[0]
    section["row_start"] = "Q"
    section["row_end"] = "R"
    section.pop('id')

    res = client.post(f"plate/{plate_id}/sections", json=section)
    assert res == 409


def test_delete(client):
    plate_id = client.get("plate/").json[0]['id']
    section = client.get(f'plate/{plate_id}/sections').json[0]
    id = section["id"]

    res = client.delete(f"section/{id}")
    assert res == 204


def test_update_not_exists(client):
    """
    Update with non-existing compound
    """
    plate_id = client.get("plate/").json[0]['id']
    section = client.get(f'plate/{plate_id}/sections').json[0]
    id = section["id"]

    res = client.put(
        f"section/{id}",
        json={"compound_name": "asdf"},
    )
    assert res == 404
