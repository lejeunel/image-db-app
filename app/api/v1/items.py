#!/usr/bin/env python3

from ...models.item import Item, ItemSchema, Tag, ItemTagAssociation
from ...models.plate import Plate
from ...models.cell import Cell
from ...models.modality import Modality
from ...models.compound import Compound, CompoundProperty
from ...models.timepoint import TimePoint
from ...models.section import Section
from ...models.stack import Stack, StackModalityAssociation


from app.utils import make_records, record_exists
from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import func
from sqlalchemy.sql.elements import literal_column

from ... import db

blp = Blueprint("Items", "Items", url_prefix="/api/v1/items", description="")


field_to_attr = {
    "id": Item.id,
    "uri": Item.uri,
    "row": Item.row,
    "col": Item.col,
    "site": Item.site,
    "plate_name": Plate.name,
    "cell_name": Cell.name,
    "cell_code": Cell.code,
    "stack_name": Stack.name,
    "modality_name": Modality.name,
    "modality_target": Modality.target,
    "compound_concentration": Section.compound_concentration,
    "compound_name": Compound.name,
    "tag": Tag.name,
    "tp_time": TimePoint.time,
    "timepoint_id": TimePoint.id,
    "section_id": Section.id,
    "plate_id": Plate.id,
}


def get_items_with_meta():
    from ... import db

    # aggregate tags (sqlite and postgre)
    if "sqlite" in db.engine.url:
        my_string_agg_fn = func.group_concat(Tag.name, ",").label('tags')
    elif "postgre" in db.engine.url:
        my_string_agg_fn = func.string_agg(Tag.name, literal_column("','")).label("tags")
    else:
        raise NotImplementedError

    items = (
        db.session.query(
            Item.id,
            Item.uri,
            Item.row,
            Item.col,
            Item.site,
            Item.chan,
            Plate.id.label("plate_id"),
            Plate.name.label("plate_name"),
            Cell.name.label("cell_name"),
            Cell.code.label("cell_code"),
            Stack.name.label("stack"),
            Modality.name.label("modality_name"),
            Modality.target.label("modality_target"),
            Section.compound_concentration.label("compound_concentration"),
            Compound.name.label("compound_name"),
            CompoundProperty.id.label("compound_property_id"),
            TimePoint.time.label("timepoint_time"),
            TimePoint.id.label("timepoint_id"),
            Section.id.label("section_id"),
            my_string_agg_fn
        )
        .join(Plate, Plate.id == Item.plate_id)
        .join(TimePoint, TimePoint.id == Item.timepoint_id)
        .join(Section, Plate.id == Section.plate_id)
        .join(Cell, Cell.id == Section.cell_id)
        .join(Stack, Stack.id == Section.stack_id)
        .join(StackModalityAssociation, StackModalityAssociation.stack_id == Stack.id)
        .join(Modality, StackModalityAssociation.modality_id == Modality.id)
        .join(Compound, Section.compound_id == Compound.id)
        .join(CompoundProperty, CompoundProperty.id == Compound.property_id)
        .join(ItemTagAssociation, ItemTagAssociation.item_id == Item.id)
        .join(Tag, ItemTagAssociation.tag_id == Tag.id)
        .filter(
            Item.chan == StackModalityAssociation.chan,
            Item.row >= Section.row_start,
            Item.row <= Section.row_end,
            Item.col >= Section.col_start,
            Item.col <= Section.col_end,
        )
        .group_by(Item.id)
        .order_by(TimePoint.time, Item.row, Item.col, Item.site)
    )

    return items


def apply_query_args(items, query_args):
    for k, v in query_args.items():
        attr = field_to_attr[k]
        items = items.filter(attr == v)
    return items


@blp.route("/")
class Items(MethodView):
    @blp.arguments(ItemSchema, location="query")
    @blp.paginate()
    @blp.response(200, ItemSchema(many=True))
    def get(self, args, pagination_parameters):
        """Get items

        Provides list of items with associated meta-data.
        """

        items = get_items_with_meta()
        items = apply_query_args(items, args)

        pagination_parameters.item_count = items.count()
        items = items.paginate(
            page=pagination_parameters.page, per_page=pagination_parameters.page_size
        ).items

        items = make_records(items, ItemSchema._declared_fields.keys())
        return items


@blp.route("/tag/<tag_name>")
class ItemTagger(MethodView):
    @blp.arguments(ItemSchema, location="query")
    @blp.paginate()
    @blp.response(200)
    def post(self, args, tag_name, pagination_parameters):
        """Tag items"""

        record_exists(Tag, tag_name, field="name")
        id = Tag.query.filter(Tag.name == tag_name).first().id

        items = get_items_with_meta()
        items = apply_query_args(items, args).all()

        assocs = [ItemTagAssociation(item_id=i.id, tag_id=id) for i in items]

        db.session.add_all(assocs)
        db.session.commit()
        return ["applied tag {}".format(tag_name)]

    @blp.arguments(ItemSchema, location="query")
    @blp.paginate()
    @blp.response(200, ItemSchema(many=True))
    def delete(self, args, tag_name, pagination_parameters):
        """Remove a tag from (set of) items"""

        record_exists(Tag, tag_name, field="name")
        tag_id = Tag.query.filter(Tag.name == tag_name).first().id

        items = get_items_with_meta()
        items = apply_query_args(items, args)
        item_ids = [i.id for i in items]
        assocs = ItemTagAssociation.query.filter(
            ItemTagAssociation.item_id.in_(item_ids)
        ).filter(ItemTagAssociation.tag_id == tag_id)
        n_tags = 0

        for a in assocs:
            db.session.delete(a)
            n_tags += 1
        db.session.commit()
