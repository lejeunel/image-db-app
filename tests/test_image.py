from urllib.parse import urlencode

def test_get_section_timepoint(client):
    res = client.get(f"plate/").json[0]
    plate_id = res['id']
    tp_ids = [tp['id'] for tp in res['timepoints']]
    section_id = client.get(f'plate/{plate_id}/sections').json[0]['id']
    for tp_id in tp_ids:
        res = client.get(f"items/?section_id={section_id}&timepoint_id={tp_id}")
        assert all([im['timepoint_id'] == tp_id for im in res.json])
        assert all([im['section_id'] == section_id for im in res.json])
        assert all([len(im['tags'].split(',')) == 1 for im in res.json])

def test_get_one_image(client):
    plate_name = 'first plate'
    params = urlencode({'plate_name': plate_name})
    res = client.get("items/?{}".format(params))
    image =  res.json[0]

    # check that joining on tags is ok
    assert len(image['tags'].split(',')) == 1

    # check get by id
    res = client.get("items/?id={}".format(image['id']))
    assert res.json[0]['id'] == image['id']

def test_get_plate(client):
    plate_name = 'first plate'
    params = urlencode({'plate_name': plate_name})
    res = client.get("items/?{}".format(params))
    assert res.json[0]['plate_name'] == plate_name


def test_get_compound(client):
    compound_name = 'compound_0'
    params = urlencode({'compound_name': compound_name})
    res = client.get("items/?{}".format(params))
    assert res.json[0]['compound_name'] == compound_name


def test_apply_tag_to_section(client):

    plate_id = client.get('plate/').json[0]['id']
    section_id = client.get(f'plate/{plate_id}/sections').json[0]['id']
    params = urlencode({'section_id': section_id})
    res = client.post("items/tag/{}?{}".format('tag_3', params))

    items = client.get("items/?{}".format(params)).json
    assert 'tag_3' in items[0]['tags']


def test_apply_existing_tag_to_section(client):

    plate_id = client.get('plate/').json[0]['id']
    section_id = client.get(f'plate/{plate_id}/sections').json[0]['id']
    params = urlencode(
        {
            'section_id': section_id,
            'tp_time': "2011-11-04T00:05:23"
        }
    )
    res = client.post("items/tag/{}?{}".format('tag2', params))


def test_delete_tag_of_section(client):

    plate_id = client.get('plate/').json[0]['id']
    section_id = client.get(f'plate/{plate_id}/sections').json[0]['id']
    params = urlencode({'section_id': section_id})
    res = client.delete("items/tag/{}?{}".format('tag1', params))

    items = client.get("items/?{}".format(params)).json
    assert 'tag1' not in items[0]['tags']


def test_apply_new_tags_with_params(client):
    plate = client.get('plate/').json[0]
    plate_id = plate['id']
    section_id = client.get(f'plate/{plate_id}/sections').json[0]['id']
    timepoint_id = plate['timepoints'][0]['id']
    params = urlencode({'section_id': section_id, 'timepoint_id': timepoint_id})

    res = client.post("items/tag/tag_3?{}".format(params))
    items = client.get("items/?{}".format(params)).json
    assert 'tag_3' in items[0]['tags']

def test_delete_one_tag(client):
    plates = client.get('plate/').json
    plate = plates[0]
    plate_id = plate['id']
    params = urlencode({'plate_id': plate_id})

    new_tag = {'name': 'newtag'}
    res = client.post('tag/', json=new_tag)

    image_before = client.get("items/?{}".format(params)).json[0]
    tags_before = image_before['tags'].split(',')

    url = "items/tag/{}?{}".format('newtag', params)
    res = client.post(url)
    res = client.delete("items/tag/newtag?{}".format(params))
    image_after = client.get("items/?{}".format(params)).json[0]

    assert all([t in image_after['tags'] for t in tags_before])
    assert 'newtag' not in image_after['tags']
