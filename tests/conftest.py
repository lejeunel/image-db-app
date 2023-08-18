#!/usr/bin/env python3

import pytest
from app.reader.base import BaseReader, validate_uri
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
            + f"file_{row}{col:02d}_w{chan}_s{site}_exp.tiff"
            for exp in ["exp1", "exp2", "exp3"]
            for tp in ["tp1", "tp2"]
            for row in ["A", "B", "C"]
            for col in range(12)
            for chan in range(1, 4)
            for site in range(2)
        ]
        self.allowed_schemes = ['scheme']

    @validate_uri()
    def list(self, uri) -> list[str]:
        """
        Return all items at uri
        """

        return [item for item in self.items if uri in item]


class TestClient(testing.FlaskClient):
    def open(self, *args, **kwargs):
        args = ("/api/v1/" + args[0],)
        return super().open(*args, **kwargs)


@pytest.fixture()
def app():
    from app import db, restapi, parser, register_blueprints, ma

    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object("app.config.test")
    with app.app_context():
        db.init_app(app)
        ma.init_app(app)
        restapi.init_app(app)
        register_blueprints(restapi)
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
    from app import db, parser
    from app.models.plate import Plate
    from app.models.modality import Modality
    from app.models.cell import Cell
    from app.models.compound import Compound, CompoundProperty
    from app.models.section import Section
    from app.models.timepoint import TimePoint
    from app.models.item import Tag, ItemTagAssociation
    from app.models.stack import Stack, StackModalityAssociation

    modalities = [
        Modality(name=n, target=t)
        for n, t in zip(
            [f"modality_{m}" for m in range(4)],
            [f"modality_target_{t}" for t in range(4)],
        )
    ]
    db.session.add_all(modalities)


    db.session.add(CompoundProperty(value="g1", type="moa_group"))  # root node
    db.session.add(CompoundProperty(value="g2", type="moa_group"))  # root node
    db.session.add_all(  # first level
        [
            CompoundProperty(value="sg3", parent_id=1, type="moa_subgroup"),
            CompoundProperty(value="sg4", parent_id=1, type="moa_subgroup"),
            CompoundProperty(value="sg5", parent_id=2, type="moa_subgroup"),
        ]
    )
    db.session.add_all(  # second level
        [
            CompoundProperty(value="t6", parent_id=5, type="target"),
            CompoundProperty(value="t7", parent_id=4, type="target"),
            CompoundProperty(value="t8", parent_id=3, type="target"),
        ]
    )
    db.session.commit()


    compounds = [
        Compound(**{"name": f"compound_{c}", "property_id": p})
        for c, p in zip(range(4), [8,7,5])
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
        StackModalityAssociation(
            stack_id=stack.id, modality_id=m.id, chan=c
        )
        for m, c in zip(modalities, range(1, 4))
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

    for t in timepoints:
        items = parser(base_uri=t.uri, plate_id=plate.id, timepoint_id=t.id)
        db.session.add_all(items)

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
