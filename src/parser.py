import re
from typing import Union

from .reader.base import BaseReader


class Parser:

    def __init__(self, reader: BaseReader):
        """Parse an endpoint for data items (files), apply filters using regular expressions

        Parameters
        ----------
        reader : BaseReader
            Reader module that implements a "list" function that retrieves all files at a URI


        """

        self.reader = reader


    def __call__(
        self,
        base_uri: str,
        additional_rex: Union[dict[str, str], None] = None,
        ignore_rex: str = "$^",
        valid_rex: str = ".*",
        **kwargs
    ) -> list[dict]:
        """Run parsing.

        Parameters
        ----------
        base_uri : str
            URI where files are parsed
        additional_rex : Union[dict[str, str], None]
            Defines additional meta-data fields to capture using regular expressions
        ignore_rex : str
            Match files to ignore.
        valid_rex : str
            Match files to include.

        Returns
        -------
        list[dict]
            List of items.

        """

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
    def __init__(self, app=None, reader=BaseReader()):
        """Simple Flask extension wrapper around Parser.

        Parameters
        ----------
        app : Flask application
        reader : File parser
        """

        if app is not None:
            self.init_app(app, reader)

    def init_app(self, app, reader: BaseReader):
        """Initialize with regular expressions taken from config"""

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
