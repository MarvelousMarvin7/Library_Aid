#!/usr/bin/env python3
""" holds class for document tag"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, ForeignKey, String


class Tag(BaseModel, Base):
    """Representation of Tag entity"""
    __tablename__ = 'tags'
    document_id = Column(String(60), ForeignKey('documents.id', ondelete='CASCADE'),
                         nullable=False)
    tag = Column(String(128), nullable=False)


    def __init__(self, *args, **kwargs):
        """initializes tags"""
        super().__init__(*args, **kwargs)
