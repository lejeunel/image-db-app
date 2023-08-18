import uuid

from app import db, ma
from sqlalchemy_utils.types.uuid import UUIDType


class Stack(db.Model):
    """
    This allows to group different modalities
    """

    __tablename__ = "stack"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    comment = db.Column(db.Text())


    def __repr__(self):
        return f"<Stack{self.name}>"


class StackModalityAssociation(db.Model):
    """
    Association model between stack and modality.
    Allows to set regular expression to match file name
    """

    __tablename__ = "stack_modality_assoc"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    stack_id = db.Column(db.ForeignKey("stack.id"), primary_key=True)
    modality_id = db.Column(db.ForeignKey("modality.id"), primary_key=True)
    chan = db.Column(db.Integer())


class StackSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Stack

    id = ma.auto_field()
    name = ma.auto_field()
    comment = ma.auto_field()
    modalities = ma.List(ma.String())
    channels = ma.List(ma.Int())
