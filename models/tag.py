#!/usr/bin/env python3
""" holds class for document tag"""
import uuid
from models.base_model import BaseModel, Base
from sqlalchemy import Column, ForeignKey, String, Enum
from sqlalchemy.orm import relationship


class DocumentTags(BaseModel, Base):
    """Contains the document tags that can be used for many documents"""
    __tablename__ = 'document_tags'
    id = Column(String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(60), ForeignKey('documents.id',
                                                    ondelete='CASCADE',
                                                    onupdate='CASCADE'
                                                    ), nullable=False)
    tag_id = Column(String(60), ForeignKey('tags.id',
                                            ondelete='CASCADE',
                                              onupdate='CASCADE'
                                              ), nullable=False)


class Tag(BaseModel, Base):
    """Representation of Tag entity"""
    __tablename__ = 'tags'
    tag = Column(Enum('AI', 'Important', 'Art',
                       'Science', 'Mathematics', 'My Document',
                         'History', 'Archaeology', 'Physics', 'Economics',
                           'Chemistry', 'Research',
                            'Technology'), nullable=True, index=True)
    documents = relationship('Document', secondary='document_tags',
                                back_populates='tags')

    def __init__(self, *args, **kwargs):
        """initializes tags"""
        super().__init__(*args, **kwargs)
