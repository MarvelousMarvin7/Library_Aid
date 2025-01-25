#!/usr/bin/env python3
""" holds class for document classification"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, ForeignKey, String, Text, Index
from sqlalchemy.orm import relationship


class Classification(BaseModel, Base):
    """Representation of Classification"""
    __tablename__ = 'classifications'
    name = Column(String(60), nullable=False)
    category_code = Column(String(60), nullable=False, index=True)
    description = Column(Text, nullable=False)
    parent_id = Column(String(60), ForeignKey('classifications.id',
                                               ondelete='SET NULL'), nullable=True)
    parent = relationship("Classification",
                           remote_side="Classification.id", backref="children")
    documents = relationship("Document", backref="classification")

    __table_args__ = (Index('my_index', "category_code"),)

    def __init__(self, *args, **kwargs):
        """initializes classification"""
        super().__init__(*args, **kwargs)
