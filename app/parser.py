from .reader.base import BaseReader
from typing import Union


import re


class Parser:
    """ """

    def __init__(self, reader: BaseReader):
        """
        Retrieves data items (files) using a base URI and filters the output
        using regular expression
        """
        self.reader = reader

    def __call__(
        self,
        base_uri: str,
        additional_rex: Union[dict[str, str], None] = None,
        ignore_rex: str = "$^",
        valid_rex: str = ".*",
        **kwargs
    ):
        """ """

        uris = self.reader.list(base_uri)
        items = [{"uri": uri} for uri in uris]

        items = [
            {"uri": uri}
            for uri in uris
            if not re.compile(ignore_rex).match(uri)
            and re.compile(valid_rex).match(uri)
        ]

        # perform regexp search on URI field using all expression and concatenate to
        # results
        if additional_rex is not None:
            for k, v in additional_rex.items():
                rex = re.compile(v)
                # find match on each URI
                matches = [rex.search(item["uri"]) for item in items]
                # append if there was a match
                items = [
                    {**r, k: match_.group(1) if matches else None}
                    for r, match_ in zip(items, matches)
                ]

        return items


class FlaskParser(Parser):
    """
    Simple extension that wraps a directory parser that retrieves
    data items using a base URI
    """

    def __init__(self, app=None, reader=BaseReader()):
        if app is not None:
            self.init_app(app, reader)

    def init_app(self, app, reader: BaseReader):
        self.app = app
        self.reader = reader
        self._parser = Parser(self.reader)
        self.parser_args = {
            "ignore_rex": app.config["IGNORE_REGEXP"],
            "valid_rex": app.config["VALID_REGEXP"],
            "additional_rex": app.config["ADDITIONAL_REGEXP"],
        }

    def __call__(self, base_uri: Union[str, list[str]], **kwargs):
        from .models import Item

        if isinstance(base_uri, str):
            base_uri = [base_uri]

        items = []
        for uri in base_uri:
            items_ = self._parser(uri, **self.parser_args)
            items += [Item(**i, **kwargs) for i in items_]

        return items
