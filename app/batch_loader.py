from .reader.s3 import S3Reader
from .reader.base import BaseReader


import re


class BatchLoader:
    """
    Post-process list of items using regexp
    """

    def __init__(
        self, reader: BaseReader
    ):
        """
        capture_regexp is a dict where keys are meta-data names, and value are regexp strings
        to capture fields from file names.
        """
        self.reader = reader

    def __call__(self, plate, timepoints):
        """
        Return list of Item
        """
        from .models import Item

        items = []
        for tp in timepoints:
            uris = self.reader(tp.uri)
            ignore_rex = re.compile(plate.ignore_regexp)
            valid_rex = re.compile(plate.valid_regexp)
            items_ = [
                {"uri": uri, 'timepoint_id': tp.id,
                 'plate_id': plate.id} for uri in uris if not ignore_rex.match(uri) and valid_rex.match(uri)
            ]

            # perform regexp search on URI field using all expression and concatenate to
            # results
            for k, v in plate.capture_regexp.items():
                rex = re.compile(v)
                # find match on each URI
                matches = [rex.search(item["uri"]) for item in items_]
                # append if there was a match
                items_ = [
                    {**r, k: match_.group(1) if matches else None}
                    for r, match_ in zip(items_, matches)
                ]
            items += [Item(**item) for item in items_]

        return items



class FlaskBatchLoader(BatchLoader):
    def __init__(self, app=None, db=None, reader=BaseReader()):
        if (app is not None) and (db is not None):
            self.init_app(app, db, reader)

    def init_app(self, app, db, reader: BaseReader):
        self.db = db
        self.reader = reader


    def __call__(self, plate, timepoints):
        items = super().__call__(plate, timepoints)
        self.db.session.add_all(items)
        self.db.session.commit()
