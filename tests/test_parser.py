#!/usr/bin/env python3
from app.reader.base import BaseReader
from app.exceptions import ParsingException

class FailingReader(BaseReader):
    """
    Dummy parser
    """

    def list(self, uri) -> list[str]:
        raise ParsingException('Could not read remote.')


def test_parser_throws_exception(app, client):
    from app.extensions import parser
    with app.app_context():
        parser.init_app(app, FailingReader())

        res = client.get('plates/').json[0]
        plate_id = res['id']
        ep = f'plates/{plate_id}/timepoints'
        res = client.post(ep,
                          json={'uri': 'scheme://bucket/exp/'})
        assert res == 400
