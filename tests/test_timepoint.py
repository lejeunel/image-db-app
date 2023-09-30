import pytest
from urllib.parse import urlencode

@pytest.mark.parametrize(
    "uri,expected_status",
    [
        ("scheme://project/exp1/tp1/", 424),
        ("badscheme://project/exp1/tp1/", 422),
    ],
)
def test_create_bad_inputs(client, uri, expected_status):
    plate_id = client.get('plates/').json[0]['id']
    data = {"plate_id": plate_id, 'uri': uri}
    res = client.post("timepoints/", json=data)
    assert res == expected_status


def test_create_good_inputs(client):
    data = {"name": "new plate"}
    res = client.post("plates/", json=data)
    assert res == 201
    plate_id = res.json['id']

    data = {'plate_id': plate_id, 'uri': "scheme://project/exp3/tp1/"}
    res = client.post("timepoints/", json=data)
    params = urlencode({'plate_id': id})
    res = client.get("items/?{}".format(params))
    assert res  == 200

def test_delete(client):
    id = client.get('timepoints/').json[0]['id']
    res = client.delete(f'timepoints/{id}')
    assert res == 204

    items = client.get('items/').json
