from flask import Flask

from app.api.v1 import register_api_blueprints
from app.views import register_views
from app.dummy_db import _populate_db
from app.reader.s3 import S3Reader
from app.reader.test import TestReader
from app.utils import datetimeformat, file_type
from app.extensions import db, bootstrap, pages, parser, ma, restapi, migrate


def create_app(mode):
    """
    Application factory
    """

    assert mode in ["test", "dev", "prod"]

    app = Flask(__name__, instance_relative_config=False)

    reader = S3Reader()
    if mode == "dev":
        app.config.from_object("app.config.dev")
    elif mode == "prod":
        app.config.from_object("app.config.prod")
    else:
        app.config.from_object("app.config.test")
        reader = TestReader()

    # set jinja filters
    app.jinja_env.filters["datetimeformat"] = datetimeformat
    app.jinja_env.filters["file_type"] = file_type
    app.jinja_env.filters["zip"] = zip


    db.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app, db)
    pages.init_app(app)
    parser.init_app(app, reader)
    ma.init_app(app)

    register_views(app, reader)

    restapi.init_app(app)
    register_api_blueprints(restapi)

    if mode == "test":
        with app.app_context():
            db.drop_all()
            db.create_all()
            _populate_db()

    return app


