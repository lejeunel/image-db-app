#!/usr/bin/env python3
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_flatpages import FlatPages
from flask_migrate import Migrate
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_mptt import mptt_sessionmaker

from .utils import datetimeformat, file_type
from .parser import FlaskParser


# subclass the db manager and insert the wrapper at session creation
class MPTTSQLAlchemy(SQLAlchemy):
    """A custom SQLAlchemy manager, to have control on session creation"""

    def create_session(self, options):
        """Override the original session factory creation"""
        Session = super().create_session(options)
        # Use wrapper from sqlalchemy_mptt that manage tree tables
        return mptt_sessionmaker(Session)

app = Flask(__name__, instance_relative_config=False)
db = MPTTSQLAlchemy()
parser = FlaskParser()
migrate = Migrate()
bootstrap = Bootstrap5()
restapi = Api()
pages = FlatPages()



def register_blueprints(restapi):
    from .api.v1 import (
        modality,
        compound,
        stack,
        plate,
        tag,
        section,
        items,
        cell,
        identity,
    )

    restapi.register_blueprint(modality.blp)
    restapi.register_blueprint(compound.blp)
    restapi.register_blueprint(stack.blp)
    restapi.register_blueprint(plate.blp)
    restapi.register_blueprint(tag.blp)
    restapi.register_blueprint(section.blp)
    restapi.register_blueprint(items.blp)
    restapi.register_blueprint(cell.blp)
    restapi.register_blueprint(identity.blp)


def create_app(mode="dev"):
    """
    Application factory
    """

    assert mode in ["dev", "prod"]

    app = Flask(__name__, instance_relative_config=False)
    if mode == "dev":
        app.config.from_object("app.config.dev")
    elif mode == "prod":
        app.config.from_object("app.config.prod")

    from . import models as mdl
    from .api.v1 import (
        cell,
        compound,
        modality,
        plate,
        section,
        stack,
        tag,
        items,
        identity,
    )
    from .views import ItemView, ListView
    from .views.image import ImageView
    from .views.plate import PlateView
    from .views.stack import StackView

    # Add detail views
    for model, schema in zip(
        [
            mdl.Modality,
            mdl.Cell,
            mdl.Compound,
            mdl.Tag,
            mdl.Section,
        ],
        [
            modality.ModalitySchema,
            cell.CellSchema,
            compound.CompoundSchema,
            tag.TagSchema,
            section.SectionSchema,
        ],
    ):
        name = model.__name__.lower()
        app.add_url_rule(
            f"/{name}/detail/<uuid:id>",
            view_func=ItemView.as_view(
                f"{name}_detail", model, schema, app.config["ITEMS_PER_PAGE"]
            ),
        )

    app.add_url_rule(
        f"/plate/detail/<uuid:id>",
        view_func=PlateView.as_view(
            f"plate_detail", mdl.Plate, plate.PlateSchema, app.config["ITEMS_PER_PAGE"]
        ),
    )
    app.add_url_rule(
        f"/stack/detail/<uuid:id>",
        view_func=StackView.as_view(
            f"stack_detail", mdl.Stack, stack.StackSchema, app.config["ITEMS_PER_PAGE"]
        ),
    )
    app.add_url_rule(
        "/image/<uuid:id>",
        view_func=ImageView.as_view(f"image_detail"),
    )

    # Add list views
    for obj in [mdl.Modality, mdl.Cell, mdl.Compound, mdl.Plate, mdl.Stack, mdl.Tag]:
        name = obj.__name__.lower()
        app.add_url_rule(
            f"/{name}/list/".lower(),
            view_func=ListView.as_view(
                f"{name}_list", obj, app.config["ITEMS_PER_PAGE"]
            ),
        )

    # Set token decoding function for AzureAD

    # set jinja filters
    app.jinja_env.filters["datetimeformat"] = datetimeformat
    app.jinja_env.filters["file_type"] = file_type
    app.jinja_env.filters["zip"] = zip

    from .views.index import bp as main_bp

    app.register_blueprint(main_bp, url_prefix="/")

    # register plugins
    db.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app, db)
    restapi.init_app(app)
    pages.init_app(app)
    parser.init_app(app)

    register_blueprints(restapi)

    return app
