import pytest
from flask import testing
from flask import Flask
from app.reader.test import TestReader
from app.dummy_db import _populate_db


class TestClient(testing.FlaskClient):
    def open(self, *args, **kwargs):
        args = ("/api/v1/" + args[0],)
        return super().open(*args, **kwargs)


@pytest.fixture()
def app():
    from app import db, restapi, parser, register_api_blueprints, ma

    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object("app.config.test")
    with app.app_context():
        db.init_app(app)
        ma.init_app(app)
        restapi.init_app(app)
        register_api_blueprints(restapi)
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
