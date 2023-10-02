import uuid

from app.extensions import db
from sqlalchemy_utils.types.uuid import UUIDType
from .mixins import UpdateMixin

class Cell(db.Model, UpdateMixin):
    __tablename__ = "cell"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100))

    def __repr__(self):
        return f"<Cell {self.name}>"

