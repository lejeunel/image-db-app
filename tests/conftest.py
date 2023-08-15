#!/usr/bin/env python3

from urllib.parse import urlparse
import pytest
from app.models import ItemTagAssociation
from app.reader.base import BaseReader
from app.exceptions import ParsingException
from flask import testing
from flask import Flask


class TestReader(BaseReader):
    """
    Dummy parser
    """

    def __init__(self):
        self.items = [
            "scheme://project/"
            + exp
            + "/"
            + tp
            + "/"
            + f"file_{row}{col:02d}_w{chan}_exp.tiff"
            for exp in ["exp1", "exp2", "exp3"]
            for tp in ["tp1", "tp2"]
            for row in ["A", "B", "C"]
            for col in range(12)
            for chan in range(1, 5)
        ]

    def __call__(self, uri):
        """
        Return all times at uri
        """
        scheme = urlparse(uri).scheme
        if scheme != "scheme":
            raise ParsingException(
                message=f"Provided scheme {scheme} not supported",
                operation="list location",
            )

        if uri[-1] != "/":
            raise ParsingException(
                message="Provided URI must end with '/'", operation="list location"
            )

        return [item for item in self.items if uri in item]


class CustomClient(testing.FlaskClient):
    def open(self, *args, **kwargs):
        args = ("/api/v1/" + args[0],)
        return super().open(*args, **kwargs)


@pytest.fixture()
def app():
    from app import db, restapi, loader, register_blueprints

    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object("app.config.test")
    with app.app_context():
        db.init_app(app)
        db.create_all()
        restapi.init_app(app)
        register_blueprints(restapi)
        loader.init_app(app, db, TestReader())
        app.test_client_class = CustomClient

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
    from app import db, loader
    from app.models import (
        Modality,
        Plate,
        Section,
        Tag,
        Cell,
        Compound,
        Stack,
        Item,
        TimePoint,
        StackModalityAssociation,
    )

    modalities = [
        Modality(name=n, target=t)
        for n, t in zip(
            [f"modality_{m}" for m in range(4)],
            [f"modality_target_{t}" for t in range(4)],
        )
    ]
    db.session.add_all(modalities)

    compounds = [
        Compound(**{"name": f"compound_{c}", "target": f"compound_target_{t}"})
        for c, t in zip(range(4), range(4))
    ]
    db.session.add_all(compounds)

    cell = Cell(name="cell_0", code="cell_code_0")
    db.session.add(cell)

    tags = [Tag(name=f"tag_{t}") for t in range(4)]
    db.session.add_all(tags)

    stack = {"name": "stack_0"}
    db.session.add(Stack(**stack))
    db.session.commit()
    stack = db.session.query(Stack).first()
    modalities = db.session.query(Modality).all()[:3]
    assocs = [
        StackModalityAssociation(stack_id=stack.id, modality_id=m.id)
        for m in modalities
    ]
    db.session.add_all(assocs)

    plate = Plate(
        name="first plate",
    )
    db.session.add(plate)
    db.session.commit()

    timepoints = [
        TimePoint(uri="scheme://project/exp1/tp1/", plate_id=plate.id),
        TimePoint(uri="scheme://project/exp1/tp2/", plate_id=plate.id),
    ]
    db.session.add_all(timepoints)
    db.session.commit()

    loader(plate, timepoints)

    base_section = {"cell_id": cell.id, "stack_id": stack.id, "plate_id": plate.id}
    sections = [
        Section(
            **{
                **base_section,
                "col_start": 1,
                "col_end": 9,
                "row_start": "A",
                "row_end": "B",
                "compound_id": compounds[0].id,
                "compound_concentration": 0.0,
            }
        ),
        Section(
            **{
                **base_section,
                "col_start": 10,
                "col_end": 12,
                "row_start": "A",
                "row_end": "B",
                "compound_id": compounds[1].id,
                "compound_concentration": 1.0,
            }
        ),
    ]

    db.session.add_all(sections)
    db.session.commit()

    # associate tags
    assocs = [
        ItemTagAssociation(item_id=item.id, tag_id=tags[0].id)
        for item in timepoints[0].items
    ]
    assocs += [
        ItemTagAssociation(item_id=item.id, tag_id=tags[1].id)
        for item in timepoints[1].items
    ]

    db.session.add_all(assocs)
    db.session.commit()
