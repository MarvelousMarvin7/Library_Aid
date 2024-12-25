#!/usr/bin/env python3
""" holds class for document classification"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, ForeignKey, String
from sqlaclhemy.orm import relationship


class Classification(BaseModel, Base):
    """Representation of Classification"""
    __tablename__ = 'classifications'
    document_id = Column(String(60), ForeignKey('documents.id', ondelete='CASCADE'),
                         nullable=False)
    name = Column(String(60), nullable=False)
    category_code = Column(String(60), nullable=False)
    description = Column(String(60), nullable=False)
    parent_id = Column(String(60), ForeignKey('classifications.id', ondelete='SET NULL'), nullable=True)
    parent = relationship("Classification", remote_side=[id], backref="children")


    def __init__(self, *args, **kwargs):
        """initializes classification"""
        super().__init__(*args, **kwargs)
