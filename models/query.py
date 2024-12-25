#!/usr/bin/env python3
""" holds class Querying of AI"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, ForeignKey, String


class Query(BaseModel, Base):
    """Representation of Query entity"""
    __tablename__ = 'queries'
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    document_id = Column(String(60), ForeignKey('documents.id', ondelete='CASCADE'),
                        nullable=False)
    query_text = Column(String(128), nullable=False)
    response_text = Column(String(128), nullable=False)


    def __init__(self, *args, **kwargs):
        """initializes Queries for AI"""
        super().__init__(*args, **kwargs)
