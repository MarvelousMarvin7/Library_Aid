#!/usr/bin/env python3
""" holds class Research Session"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import relationship
import uuid


class SessionDocuments(Base):
    """Establishes the many-to-many relatioinship
    between document and research session
    """
    __tablename__ = 'session_documents'
    id = Column(String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    research_session_id = Column('research_session_id',
                                    String(60),
                                    ForeignKey('research_sessions.id',
                                                ondelete='CASCADE',
                                                onupdate='CASCADE'
                                                )
                                )
    document_id = Column('document_id',
                          String(60),
                            ForeignKey('documents.id',
                                        ondelete='CASCADE',
                                        onupdate='CASCADE'
                                        )
                        )


class ResearchSession(BaseModel, Base):
    """Representation of Research Session """
    __tablename__ = 'research_sessions'
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    session_start = Column(DateTime, nullable=False)
    session_title = Column(Text, nullable=False)
    session_end = Column(DateTime, nullable=False)
    queries = relationship("Query", backref="research_session")
    documents_accessed = relationship('Document',
                                        secondary='session_documents',
                                        back_populates='research_sessions'
                                    )


    def __init__(self, *args, **kwargs):
        """initializes Research Session"""
        super().__init__(*args, **kwargs)
