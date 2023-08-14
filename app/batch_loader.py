from .reader.s3 import S3Reader
from .reader.base import BaseReader


import re


class BatchLoader:
    """
    Post-process list of items using regexp
    """

    def __init__(
        self, reader: BaseReader, ignore_regexp, valid_regexp, capture_regexp: dict = {}
    ):
        """
        capture_regexp is a dict where keys are meta-data names, and value are regexp strings
        to capture fields from file names.
        """
        self.reader = reader
        self.ignore_regexp = ignore_regexp
        self.valid_regexp = valid_regexp
        self.capture_regexp = capture_regexp

    def __call__(self, uri):
        """
        Return list of URIs that match regexps
        """
        items = self.reader(uri)
        ignore_rex = re.compile(self.ignore_regexp)
        valid_rex = re.compile(self.valid_regexp)
        results = [
            {"uri": i} for i in items if not ignore_rex.match(i) and valid_rex.match(i)
        ]

        # perform regexp search on URI field using all expression and concatenate to
        # results
        for k, v in self.capture_regexp.items():
            rex = re.compile(v)
            # find match on each URI
            matches = [rex.search(r["uri"]) for r in results]
            # append if there was a match
            results = [
                {**r, k: match_.group(1) if matches else None}
                for r, match_ in zip(results, matches)
            ]

        return results


class FlaskBatchLoader:
    def __init__(self, app=None, reader=BaseReader()):
        if app is not None:
            self.init_app(app, reader)

    def init_app(self, app, reader: BaseReader):
        self.reader = reader
        self.loader = BatchLoader(
            self.reader,
            app.config["IGNORE_REGEXP"],
            app.config["VALID_REGEXP"],
            app.config["CAPTURE_REGEXP_DICT"],
        )

    def __call__(self, uri):
        return self.loader(uri)
