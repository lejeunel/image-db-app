#!/usr/bin/env python3
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_flatpages import FlatPages
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_mptt import mptt_sessionmaker
from app.parser import FlaskParser

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
ma = Marshmallow()
