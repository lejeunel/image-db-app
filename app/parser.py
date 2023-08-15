from .reader.s3 import S3Reader
from .reader.base import BaseReader


import re


class Parser:
    """
    Post-process list of items using regexp
    """

    def __init__(self, reader: BaseReader):
        """
        capture_regexp is a dict where keys are meta-data names, and value are regexp strings
        to capture fields from file names.
        """
        self.reader = reader

    def __call__(
        self,
        base_uri: str,
        ignore_regexp: str,
        valid_regexp: str,
        site_regexp: str,
        row_regexp: str,
        col_regexp: str,
        **kwargs
    ):
        """
        Return list of Item
        """

        uris = self.reader(base_uri)
        ignore_rex = re.compile(ignore_regexp)
        valid_rex = re.compile(valid_regexp)
        items = [
            {"uri": uri, **kwargs}
            for uri in uris
            if not ignore_rex.match(uri) and valid_rex.match(uri)
        ]

        # perform regexp search on URI field using all expression and concatenate to
        # results
        for k, v in [
            ("site", re.compile(site_regexp)),
            ("col", re.compile(col_regexp)),
            ("row", re.compile(row_regexp)),
        ]:
            rex = re.compile(v)
            # find match on each URI
            matches = [rex.search(item["uri"]) for item in items]
            # append if there was a match
            items = [
                {**r, k: match_.group(1) if matches else None}
                for r, match_ in zip(items, matches)
            ]

        return items


class FlaskParser:
    def __init__(self, app=None, db=None, reader=BaseReader()):
        if (app is not None) and (db is not None):
            self.init_app(app, db, reader)

    def init_app(self, app, db, reader: BaseReader):
        self.app = app
        self.db = db
        self.reader = reader
        self.parser = Parser(self.reader)

    def __call__(self, plate, timepoints):
        from .models import Item
        items = [
            self.parser(
                timepoint.uri,
                plate.ignore_regexp,
                plate.valid_regexp,
                plate.site_regexp,
                plate.row_regexp,
                plate.col_regexp,
                plate_id=plate.id,
                timepoint_id=timepoint.id,
            )
            for timepoint in timepoints
        ]
        items = [Item(**i) for items_ in items for i in items_]

        self.db.session.add_all(items)
        self.db.session.commit()
