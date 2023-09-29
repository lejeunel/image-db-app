import pytest
from flask import testing
from flask import Flask
from flask_smorest.pagination import PaginationMixin
from app.reader.test import TestReader
from app.dummy_db import _populate_db
from unittest.mock import patch, PropertyMock

#

class TestClient(testing.FlaskClient):
    def open(self, *args, **kwargs):
        args = ("/api/v1/" + args[0],)
        # return super().open(*args, page_size=10e5, max_page_size=10e5, **kwargs)
        return super().open(*args, **kwargs)


@pytest.fixture()
def app():
    from app import db, restapi, parser, register_api_blueprints, ma

    app = Flask(__name__, instance_relative_config=False)

    # # make api return all items by patching class attributes
    # with patch.object(PaginationMixin, "DEFAULT_PAGINATION_PARAMETERS", new_callable=PropertyMock) as attr_mock:
    #     attr_mock.return_value = {"page": 1, "page_size": 100000, "max_page_size": 1000000}

    app.config.from_object("app.config.test")
    with app.app_context():
        db.init_app(app)
        ma.init_app(app)
        restapi.init_app(app)
        register_api_blueprints(app, restapi)
        parser.init_app(app, TestReader())

        db.create_all()
        app.test_client_class = TestClient

        yield app

        # clean up / reset resources here
        db.drop_all()


@pytest.fixture()
def client(app):
    with app.app_context():
        client = app.test_client()
        yield client


@pytest.fixture(autouse=True)
def populate_db(app):
    _populate_db()
