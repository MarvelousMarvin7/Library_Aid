#!/usr/bin/env python3
""" holds class for document abstracts for AI"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, ForeignKey, String, Text


class Abstract(BaseModel, Base):
    """Representation of abstracts entity for AI"""
    __tablename__ = 'abstracts'
    document_id = Column(String(60), ForeignKey('documents.id', ondelete='CASCADE'),
                         nullable=False)
    abstract_text = Column(Text, nullable=False)


    def __init__(self, *args, **kwargs):
        """initializes abstracts for AI"""
        super().__init__(*args, **kwargs)
