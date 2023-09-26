#!/usr/bin/env python3
from src import create_app, db
import re
from rich import print

app = create_app('prod')

from src.models.item import Item

with app.app_context():
    items = db.session.query(Item).all()
    n_items = len(items)
    rex = re.compile(app.config['ADDITIONAL_REGEXP']['chan'])
    for i, item in enumerate(items):
        uri = item.uri
        chan = int(rex.search(item.uri).group(1))
        print(f'{i+1}/{n_items}: {item.uri} -> chan {chan}')
        item.chan = chan
    db.session.commit()
