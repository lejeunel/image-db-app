#!/usr/bin/env python3

from ... import models as mdl
from ... import schemas as sch

from app.utils import record_exists
from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import func
from sqlalchemy.sql.elements import literal_column
from flask import current_app

from ... import db


blp = Blueprint("Items", "Items", url_prefix="/api/v1/items", description="")
blp.DEFAULT_PAGINATION_PARAMETERS = {
    "page": 1,
    "page_size": current_app.config["API_ITEMS_PAGE_SIZE"],
    "max_page_size": current_app.config["API_ITEMS_MAX_PAGE_SIZE"],
}


def get_items_with_meta():
    from ... import db

    # aggregate tags (sqlite and postgre)
    url = str(db.engine.url)
    if "sqlite" in url:
        my_string_agg_fn = func.group_concat(mdl.Tag.name, ",").label("tags")
    elif "postgre" in url:
        my_string_agg_fn = func.string_agg(mdl.Tag.name, literal_column("','")).label(
            "tags"
        )
    else:
        raise NotImplementedError

    items = (
        db.session.query(
            mdl.Item.id,
            mdl.Item.uri,
            mdl.Item.row,
            mdl.Item.col,
            mdl.Item.site,
            mdl.Item.chan,
            mdl.Plate.id.label("plate_id"),
            mdl.Plate.name.label("plate_name"),
            mdl.Cell.name.label("cell_name"),
            mdl.Cell.code.label("cell_code"),
            mdl.Stack.name.label("stack"),
            mdl.Modality.name.label("modality_name"),
            mdl.Modality.target.label("modality_target"),
            mdl.Section.compound_concentration.label("compound_concentration"),
            mdl.Compound.name.label("compound_name"),
            mdl.CompoundProperty.id.label("compound_property_id"),
            mdl.TimePoint.time.label("timepoint_time"),
            mdl.TimePoint.id.label("timepoint_id"),
            mdl.Section.id.label("section_id"),
            my_string_agg_fn,
        )
        .join(mdl.Plate, mdl.Plate.id == mdl.Item.plate_id)
        .join(mdl.TimePoint, mdl.TimePoint.id == mdl.Item.timepoint_id)
        .outerjoin(mdl.Section, mdl.Plate.id == mdl.Section.plate_id)
        .join(mdl.Cell, mdl.Cell.id == mdl.Section.cell_id)
        .join(mdl.Stack, mdl.Stack.id == mdl.Section.stack_id)
        .join(mdl.StackModalityAssociation, mdl.StackModalityAssociation.stack_id == mdl.Stack.id)
        .join(mdl.Modality, mdl.StackModalityAssociation.modality_id == mdl.Modality.id)
        .join(mdl.Compound, mdl.Section.compound_id == mdl.Compound.id)
        .join(mdl.CompoundProperty, mdl.CompoundProperty.id == mdl.Compound.property_id)
        .outerjoin(mdl.ItemTagAssociation, mdl.ItemTagAssociation.item_id == mdl.Item.id)
        .outerjoin(mdl.Tag, mdl.ItemTagAssociation.tag_id == mdl.Tag.id)
        .filter(
            mdl.Item.chan == mdl.StackModalityAssociation.chan,
            mdl.Item.row >= mdl.Section.row_start,
            mdl.Item.row <= mdl.Section.row_end,
            mdl.Item.col >= mdl.Section.col_start,
            mdl.Item.col <= mdl.Section.col_end,
        )
        .order_by(mdl.TimePoint.time, mdl.Item.row, mdl.Item.col, mdl.Item.site, mdl.Item.chan)
        .group_by(mdl.Item.id, mdl.Plate.id, mdl.TimePoint.id, mdl.Section.id, mdl.Cell.id,
                  mdl.Stack.id, mdl.StackModalityAssociation.id, mdl.Modality.id,
                  mdl.Compound.id, mdl.CompoundProperty.id)
    )

    return items


def apply_query_args(db, items, query_args):

    for k, v in query_args.items():
        # fetch all registered models
        models = [mapper.class_ for mapper in db.Model.registry.mappers]

        # case 1: left of underscore is the name of table/model
        # case 2: tags -> use regexp
        # case 3: no underscore -> use table "item"
        # case 4: table/model combination is invalid, check for compound property
        if "_" in k:
            elements = k.split("_")
            table_name = elements[0]
            field = "_".join(elements[1:])
        elif k == 'tags':
            table_name = 'tag'
            field = 'name'
            items = items.subquery()
            # tag name can be followed by a comma (when it has other tags)
            items = db.session.query(items).filter(items.c.tags.regexp_match(f'({v},)|({v}$)'))
        else:
            table_name = "item"
            field = k

        model = [m for m in models if m.__tablename__ == table_name][0]
        model_has_attr = hasattr(model, field)
        if model_has_attr:
            field = getattr(model, field)
            items = items.filter(field == v)
        else:
            # case 4: fetch in compound_property for matching attribute
            compound_property = mdl.CompoundProperty.query.filter(
                mdl.CompoundProperty.type == field
            ).filter(mdl.CompoundProperty.value == v)

            found_matching_property = compound_property.count() > 0
            if found_matching_property:
                matching_property = compound_property.first()
                items = items.filter(
                    mdl.CompoundProperty.left >= matching_property.left
                ).filter(mdl.CompoundProperty.right <= matching_property.right)
            else:
                items = items.filter(False)

    return items


@blp.route("/")
class Items(MethodView):
    @blp.arguments(sch.ItemSchema, location="query")
    @blp.paginate()
    @blp.response(200, sch.ItemSchema(many=True))
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
    @blp.arguments(sch.ItemSchema, location="query")
    @blp.paginate()
    @blp.response(200)
    def post(self, args, tag_name, pagination_parameters):
        """Tag items"""

        record_exists(db, mdl.Tag, tag_name, field="name")
        id = db.session.query(mdl.Tag).filter(mdl.Tag.name == tag_name).first().id

        items = get_items_with_meta()
        items = apply_query_args(db, items, args).all()

        pagination_parameters.item_count = len(items)
        assocs = [mdl.ItemTagAssociation(item_id=i.id, tag_id=id) for i in items]

        db.session.add_all(assocs)
        db.session.commit()
        return ["applied tag {}".format(tag_name)]

    @blp.arguments(sch.ItemSchema, location="query")
    @blp.paginate()
    @blp.response(200, sch.ItemSchema(many=True))
    def delete(self, args, tag_name, pagination_parameters):
        """Remove a tag from (set of) items"""

        record_exists(db, mdl.Tag, tag_name, field="name")
        tag_id = db.session.query(mdl.Tag).filter(mdl.Tag.name == tag_name).first().id

        items = get_items_with_meta()
        items = apply_query_args(db, items, args)
        pagination_parameters.item_count = items.count()

        item_ids = [i.id for i in items]
        assocs = (
            db.session.query(mdl.ItemTagAssociation)
            .filter(mdl.ItemTagAssociation.item_id.in_(item_ids))
            .filter(mdl.ItemTagAssociation.tag_id == tag_id)
            .delete()
        )

        db.session.commit()
