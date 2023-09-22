import uuid

from app import db, ma
from app.models.compound import CompoundProperty
from .utils import _concat_properties
from marshmallow import post_dump, pre_dump, pre_load, post_load
from sqlalchemy_utils.types.uuid import UUIDType


class Item(db.Model):
    """
    Basic object that refers to a resource (file)
    """

    __tablename__ = "item"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    uri = db.Column(db.String(300))
    row = db.Column(db.String(1))
    col = db.Column(db.Integer)
    site = db.Column(db.Integer)
    chan = db.Column(db.Integer)
    plate_id = db.Column(db.ForeignKey("plate.id"))
    timepoint_id = db.Column(db.ForeignKey("timepoint.id"))


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Item
        additional = (
            "plate_name",
            "cell_name",
            "cell_code",
            "stack_name",
            "modality_name",
            "modality_target",
            "compound_concentration",
            "compound_name",
            "compound_property_id",
            "compound_moa_group",
            "compound_moa_subgroup",
            "compound_target",
            "timepoint_time",
            "timepoint_id",
            "section_id",
            "tags",
        )

    @post_dump()
    def concat_compound_props(self, data, **kwargs):
        data = _concat_properties(
            db,
            CompoundProperty,
            data,
            prefix="compound_",
            id_field="compound_property_id",
            **kwargs,
        )
        return data



class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    comment = db.Column(db.Text())

    def __repr__(self):
        return f"<Tag {self.name}>"


class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tag


class ItemTagAssociation(db.Model):
    """
    Association model between item and tag.
    """

    __tablename__ = "item_tag_assoc"
    __table_args__ = (db.UniqueConstraint("item_id", "tag_id"),)
    item_id = db.Column(db.ForeignKey("item.id"), primary_key=True)
    tag_id = db.Column(db.ForeignKey("tag.id"), primary_key=True)

    item = db.relationship("Item", foreign_keys=[item_id])
    tag = db.relationship("Tag", foreign_keys=[tag_id])
