from app import db, ma
from sqlalchemy_utils.types.uuid import UUIDType
import uuid
from sqlalchemy.ext.associationproxy import association_proxy

class Modality(db.Model):
    __tablename__ = "modality"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    target = db.Column(db.String(100))
    comment = db.Column(db.Text())

    def __repr__(self):
        return f"<Modality {self.name}>"

class ModalitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Modality
