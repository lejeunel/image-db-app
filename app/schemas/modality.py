#!/usr/bin/env python3
from app import ma
from ..models.modality import Modality


class ModalitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Modality
