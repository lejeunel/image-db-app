#!/usr/bin/env python3
from src import create_app, db
import re
from rich import print

app = create_app('prod')

from src.models.stack import StackModalityAssociation

with app.app_context():
    assocs = db.session.query(StackModalityAssociation).all()
    rex = re.compile('^.*([0-9]).*$')
    for a in assocs:
        chan = rex.search(a.regexp).group(1)
        a.chan = int(chan)
        db.session.commit()
