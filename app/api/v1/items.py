#!/usr/bin/env python3

from app.schema import ItemsSchema
from app.utils import make_records, record_exists
from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import func
from sqlalchemy.sql.elements import literal_column

from ... import db
from ...models import (
    Cell,
    Compound,
    Item,
    ItemTagAssociation,
    Modality,
    Plate,
    Section,
    Stack,
    StackModalityAssociation,
    Tag,
    TimePoint,
)

blp = Blueprint("Items", "Items", url_prefix="/api/v1/items", description="")


field_to_attr = {
    "id": Item.id,
    "uri": Item.uri,
    "row": Item.row,
    "col": Item.col,
    "site": Item.site,
    "batch_name": Plate.name,
    "cell_name": Cell.name,
    "cell_code": Cell.code,
    "stack_name": Stack.name,
    "modality_name": Modality.name,
    "modality_target": Modality.target,
    "compound_concentration": Section.compound_concentration,
    "compound_name": Compound.name,
    "compound_target": Compound.target,
    "compound_moa_group": Compound.moa_group,
    "compound_moa_subgroup": Compound.moa_subgroup,
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
            Plate.name.label("plate_name"),
            Cell.name.label("cell_name"),
            Cell.code.label("cell_code"),
            Stack.name.label("stack"),
            Modality.name.label("modality_name"),
            Modality.target.label("modality_target"),
            Section.compound_concentration.label("compound_concentration"),
            Compound.name.label("compound_name"),
            Compound.target.label("compound_target"),
            Compound.moa_group.label("compound_moa_group"),
            Compound.moa_subgroup.label("compound_moa_subgroup"),
            TimePoint.time.label("timepoint_time"),
            TimePoint.id.label("timepoint_id"),
            Section.id.label("section_id"),
            Plate.id.label("plate_id"),
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
        .filter(
            Item.uri.like(StackModalityAssociation.regexp),
            Item.row >= Section.row_start,
            Item.row <= Section.row_end,
            Item.col >= Section.col_start,
            Item.col <= Section.col_end,
        )
        .group_by(Item.id)
        .order_by(TimePoint.time, Item.row, Item.col, Item.site, Modality.name)
    )

    return items


def append_tag_row(item):
    assocs = ItemTagAssociation.query.filter_by(item_id=item["id"]).all()
    tags = ",".join([a.tag.name for a in assocs])
    item["tags"] = tags
    return item


def append_tag_col(items):
    for item in items:
        im = append_tag_row(item)
    return items


def apply_query_args(items, query_args):
    for k, v in query_args.items():
        attr = field_to_attr[k]
        items = items.filter(attr == v)
    return items


@blp.route("/")
class Items(MethodView):
    @blp.arguments(ItemsSchema, location="query")
    @blp.paginate()
    @blp.response(200, ItemsSchema(many=True))
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

        items = make_records(items, ItemsSchema._declared_fields.keys())
        items = append_tag_col(items)
        return items


@blp.route("/tag/<tag_name>")
class ItemTagger(MethodView):
    @blp.arguments(ItemsSchema, location="query")
    @blp.paginate()
    @blp.response(200)
    def post(self, args, tag_name, pagination_parameters):
        """Tag items"""

        record_exists(Tag, tag_name, field="name")
        id = Tag.query.filter(Tag.name == tag_name).first().id

        items = get_items_with_meta()
        items = apply_query_args(items, args).all()

        assocs = [ItemTagAssociation(item_id=i.id, tag_id=id) for i in items]

        n_tagged = 0
        for a in assocs:
            try:
                db.session.add(a)
                db.session.commit()
            except:
                db.session.rollback()
            else:
                n_tagged += 1
        return ["applied tag {} to {} items".format(tag_name, n_tagged)]

    @blp.arguments(ItemsSchema, location="query")
    @blp.paginate()
    @blp.response(200, ItemsSchema(many=True))
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
