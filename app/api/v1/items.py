#!/usr/bin/env python3

from ...models.item import Item, ItemSchema, Tag, ItemTagAssociation
from ...models.plate import Plate
from ...models.cell import Cell
from ...models.modality import Modality
from ...models.compound import Compound, CompoundProperty
from ...models.timepoint import TimePoint
from ...models.section import Section
from ...models.stack import Stack, StackModalityAssociation


from app.utils import record_exists
from flask.views import MethodView
from app.api import Blueprint
from sqlalchemy import func
from sqlalchemy.sql.elements import literal_column
from sqlalchemy import text
from flask import current_app

from ... import db


blp = Blueprint("Items", "Items", url_prefix="/api/v1/items", description="")


def get_items_with_meta():
    from ... import db

    # aggregate tags (sqlite and postgre)
    if "sqlite" in db.engine.url:
        my_string_agg_fn = func.group_concat(Tag.name, ",").label("tags")
    elif "postgre" in db.engine.url:
        my_string_agg_fn = func.string_agg(Tag.name, literal_column("','")).label(
            "tags"
        )
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
            my_string_agg_fn,
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


def apply_query_args(db, items, query_args):
    # TODO use nested set logic to filter

    for k, v in query_args.items():
        # fetch all registered models
        models = [mapper.class_ for mapper in db.Model.registry.mappers]

        if "_" in k:
            elements = k.split("_")
            table_name = elements[0]
            field = "_".join(elements[1:])
        else:
            table_name = "item"
            field = k

        model = [m for m in models if m.__tablename__ == table_name][0]
        model_has_attr = hasattr(model, field)
        if model_has_attr:
            field = getattr(model, field)
            items = items.filter(field == v)
        else:
            # check in compound properties
            compound_property = CompoundProperty.query.filter(
                CompoundProperty.type == field
            ).filter(CompoundProperty.value == v)

            found_matching_property = compound_property.count() > 0
            if found_matching_property:
                matching_property = compound_property.first()
                items = items.filter(
                    CompoundProperty.left >= matching_property.left
                ).filter(CompoundProperty.right <= matching_property.right)
            else:
                items = items.filter(False)

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
        items = apply_query_args(db, items, args)

        pagination_parameters.item_count = items.count()
        items = items.paginate(
            page=pagination_parameters.page, per_page=pagination_parameters.page_size
        ).items

        return items


@blp.route("/tag/<tag_name>")
class ItemTagger(MethodView):
    @blp.arguments(ItemSchema, location="query")
    @blp.paginate()
    @blp.response(200)
    def post(self, args, tag_name, pagination_parameters):
        """Tag items"""

        record_exists(db, Tag, tag_name, field="name")
        id = db.session.query(Tag).filter(Tag.name == tag_name).first().id

        items = get_items_with_meta()
        items = apply_query_args(db, items, args).all()

        pagination_parameters.item_count = len(items)
        assocs = [ItemTagAssociation(item_id=i.id, tag_id=id) for i in items]

        db.session.add_all(assocs)
        db.session.commit()
        return ["applied tag {}".format(tag_name)]

    @blp.arguments(ItemSchema, location="query")
    @blp.paginate()
    @blp.response(200, ItemSchema(many=True))
    def delete(self, args, tag_name, pagination_parameters):
        """Remove a tag from (set of) items"""

        record_exists(db, Tag, tag_name, field="name")
        tag_id = db.session.query(Tag).filter(Tag.name == tag_name).first().id

        items = get_items_with_meta()
        items = apply_query_args(db, items, args)
        pagination_parameters.item_count = items.count()

        item_ids = [i.id for i in items]
        assocs = (
            db.session.query(ItemTagAssociation)
            .filter(ItemTagAssociation.item_id.in_(item_ids))
            .filter(ItemTagAssociation.tag_id == tag_id)
            .delete()
        )

        db.session.commit()
