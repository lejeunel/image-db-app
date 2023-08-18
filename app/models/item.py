import uuid

from app import db, ma
from app.models.compound import CompoundProperty
from marshmallow import post_dump
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



class ItemSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Item

    id = ma.auto_field()
    uri = ma.auto_field()
    row = ma.auto_field()
    col = ma.auto_field()
    site = ma.auto_field()
    chan = ma.auto_field()
    plate_id = ma.auto_field()


    plate_name = ma.String()
    cell_name = ma.String()
    cell_code = ma.String()
    stack_name = ma.String()
    modality_name = ma.String()
    modality_target = ma.String()
    compound_concentration = ma.Float()
    compound_name = ma.String()
    compound_property_id = ma.Int()
    tp_time = ma.DateTime()
    timepoint_id = ma.UUID()
    section_id = ma.UUID()
    tags = ma.String()

    @post_dump()
    def concat_compound_props(
        self, data, prefix="compound_", id_field="compound_property_id", **kwargs
    ):
        # get properties of all ancestors
        properties = (
            CompoundProperty.query.get(data["compound_property_id"])
            .path_to_root()
            .all()
        )
        properties = [(p.type._name_, p.name) for p in properties]

        # convert to dict and concatenate prefix
        properties = {prefix + f"{p[0]}": p[1] for p in properties}

        data = {**data, **properties}
        return data


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    comment = db.Column(db.Text())

    def __repr__(self):
        return f"<Tag {self.name}>"


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
