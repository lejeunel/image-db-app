import uuid

from app import db, ma
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
