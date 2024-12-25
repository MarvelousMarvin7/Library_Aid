#!/usr/bin/env python3
""" holds class Research Session"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, ForeignKey, String, Table, DateTime
from sqlalchemy.orm import relationship

session_documents = Table(
    'session_documents',
    Base.metadata,
    Column('session_id', String(60), ForeignKey('research_sessions.id',
                                                 ondelete='CASCADE')),
    Column('document_id', String(60), ForeignKey('documents.id',
                                                  ondelete='CASCADE'))
)


class ResearchSession(BaseModel, Base):
    """Representation of Research Session """
    __tablename__ = 'research_sessions'
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    session_start = Column(DateTime, nullable=False)
    session_end = Column(DateTime, nullable=False)
    documents_accessed = relationship('Document', secondary=session_documents,
                                       back_populates='accessed_by_sessions')

    
    def __init__(self, *args, **kwargs):
        """initializes Research Session"""
        super().__init__(*args, **kwargs)
