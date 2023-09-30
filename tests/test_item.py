from urllib.parse import urlencode

def test_get_section_timepoint(client):
    res = client.get(f"plates/").json[0]
    plate_id = res['id']
    section_id = client.get(f'plates/{plate_id}/sections').json[0]['id']
    timepoints = client.get(f'plates/{plate_id}/timepoints').json
    timepoints_id = [t['id'] for t in timepoints]
    for tp_id in timepoints_id:
        res = client.get(f"items/?section_id={section_id}&timepoint_id={tp_id}")
        assert all([im['timepoint_id'] == tp_id for im in res.json])
        assert all([im['section_id'] == section_id for im in res.json])

def test_get_images(client):
    res = client.get("items/")
    assert res == 200

def test_get_image_by_tag(client):
    res = client.get("items/?tags=tag_1")
    assert all(['tag_1' in r['tags'] for r in res.json])
    assert all(['tag_2' in r['tags'] for r in res.json])
    assert all(['tag_0' not in r['tags'] for r in res.json])


def test_get_image_by_id(client):
    res = client.get("items/")
    item_id = res.json[0]['id']
    assert res == 200

    res = client.get("items/?id={}".format(item_id))
    assert res.json[0]['id'] == item_id

def test_get_by_properties_should_retrieve_subproperties(client):
    params = urlencode({'compound_moa_group': 'g1'})
    res = client.get("items/?{}".format(params))
    assert all([r['compound_moa_group'] == 'g1' for r in res.json])
    assert any([r['compound_moa_subgroup'] == 'sg3' for r in res.json])
    assert any([r['compound_moa_subgroup'] == 'sg4' for r in res.json])

def test_get_by_non_existing_properties_should_fail(client):
    params = urlencode({'compound_moa_group': 'g3'})
    res = client.get("items/?{}".format(params))
    assert len(res.json) == 0

def test_get_compound(client):
    compound_name = 'compound_0'
    params = urlencode({'compound_name': compound_name})
    res = client.get("items/?{}".format(params))
    assert res.json[0]['compound_name'] == compound_name


def test_apply_tag_to_section(client):

    plate_id = client.get('plates/').json[0]['id']
    section_id = client.get(f'plates/{plate_id}/sections').json[0]['id']
    params = urlencode({'section_id': section_id})
    res = client.post("items/tag/{}?{}".format('tag_3', params))

    items = client.get("items/?{}".format(params)).json
    assert 'tag_3' in items[0]['tags']


def test_apply_existing_tag_to_section(client):

    plate_id = client.get('plates/').json[0]['id']
    section_id = client.get(f'plates/{plate_id}/sections').json[0]['id']
    params = urlencode(
        {
            'section_id': section_id,
            'timepoint_time': "2011-11-04T00:05:23"
        }
    )
    res = client.post("items/tag/{}?{}".format('tag2', params))


def test_delete_tag_of_section(client):

    plate_id = client.get('plates/').json[0]['id']
    section_id = client.get(f'plates/{plate_id}/sections').json[0]['id']
    params = urlencode({'section_id': section_id})
    res = client.delete("items/tag/{}?{}".format('tag1', params))

    items = client.get("items/?{}".format(params)).json
    assert 'tag1' not in items[0]['tags']


def test_apply_new_tags_with_params(client):
    plate = client.get('plates/').json[0]
    plate_id = plate['id']
    section_id = client.get(f'plates/{plate_id}/sections').json[0]['id']
    timepoint_id = client.get(f'plates/{plate_id}/timepoints').json[0]['id']
    params = urlencode({'section_id': section_id, 'timepoint_id': timepoint_id})

    res = client.post("items/tag/tag_3?{}".format(params))
    items = client.get("items/?{}".format(params)).json
    assert 'tag_3' in items[0]['tags']

def test_untag(client):
    plates = client.get('plates/').json
    plate_id = plates[0]['id']
    params = urlencode({'plate_id': plate_id})

    new_tag = {'name': 'newtag'}
    res = client.post('tags/', json=new_tag)

    image_before = client.get("items/?{}".format(params)).json[0]
    tags_before = image_before['tags']

    url = "items/tag/{}?{}".format('newtag', params)
    res = client.post(url)
    res = client.delete("items/tag/newtag?{}".format(params))
    image_after = client.get("items/?{}".format(params)).json[0]

    assert all([t in image_after['tags'] for t in tags_before])
    assert 'newtag' not in image_after['tags']


