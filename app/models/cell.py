import uuid

from app import db
from sqlalchemy_utils.types.uuid import UUIDType


class Cell(db.Model):
    __tablename__ = "cell"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    code = db.Column(db.String(100))

    def __repr__(self):
        return f"<Cell {self.name}>"

