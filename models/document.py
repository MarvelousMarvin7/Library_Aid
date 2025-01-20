#!/usr/bin/env python3
""" holds class Document"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, Enum, ForeignKey, String, Text, Index
from sqlalchemy.orm import relationship
import models


class Document(BaseModel, Base):
    """Representation of Document """
    __tablename__ = 'documents'
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    
    title = Column(String(128), nullable=False)
    description = Column(String(1024), nullable=True)
    file_path = Column(String(128), nullable=False)
    file_type = Column(Enum('PDF', 'TXT', 'JPEG', 'DOCX', 'PNG',
                             name='file_types'), nullable=False)
    image_url = Column(String(128), nullable=True)
    classification_code = Column(String(128), nullable=True)
    abstract = Column(Text, nullable=True)
    abstracts = relationship("Abstract", backref="document", cascade="all, delete")
    classifications = relationship("Classification", backref="document",
                                    cascade="all, delete")
    research_sessions = relationship('ResearchSession',
                                        secondary='session_documents',
                                        back_populates='documents_accessed'
                                    )
    tags = relationship('Tag', secondary='document_tags', back_populates='documents')
    
    __table_args__ = (Index('my_index', "title", "classification_code"),)

    def to_dict(self):
        """Extend the BaseModel's to_dict to include tags."""
        doc_dict = super().to_dict()
        doc_dict['tags'] = [tag.tag for tag in self.tags]
        return doc_dict

    def __init__(self, *args, **kwargs):
        """initializes Document"""
        super().__init__(*args, **kwargs)
