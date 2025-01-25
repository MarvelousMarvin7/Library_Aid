#!/usr/bin/env python3
""" holds class Querying of AI"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, ForeignKey, String, Text


class Query(BaseModel, Base):
    """Representation of Query entity"""
    __tablename__ = 'queries'
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    research_session_id = Column(String(60), ForeignKey('research_sessions.id', ondelete='CASCADE'),
                                                        nullable=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)


    def __init__(self, *args, **kwargs):
        """initializes Queries for AI"""
        super().__init__(*args, **kwargs)
