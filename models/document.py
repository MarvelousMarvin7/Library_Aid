#!/usr/bin/env python3
""" holds class Document"""
from models.base_model import BaseModel, Base
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship


class Document(BaseModel, Base):
    """Representation of Document """
    __tablename__ = 'documents'
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    title = Column(String(128), nullable=False)
    description = Column(String(1024), nullable=True)
    file_path = Column(String(128), nullable=False)
    file_type = Column(String(128), nullable=False)
    image_url = Column(String(128), nullable=True)
    classification_code = Column(String(128), nullable=False)
    tag = Column(String(128), nullable=False)
    abstract = Column(Text, nullable=False)
    abstracts = relationship("Abstract", backref="document", cascade="all, delete")
    tags = relationship("Tag", backref="document", cascade="all, delete")
    classifications = relationship("Classification", backref="document", cascade="all, delete")

    def __init__(self, *args, **kwargs):
        """initializes Document"""
        super().__init__(*args, **kwargs)
