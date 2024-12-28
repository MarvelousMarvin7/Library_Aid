#!/usr/bin/env python3
""" holds class Notification"""
from models.base_model import BaseModel, Base
from sqlalchemy import Boolean, Column, ForeignKey, String


class Notification(BaseModel, Base):
    """Representation of Notification"""
    __tablename__ = 'notifications'
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    message = Column(String(128), nullable=False)
    is_read = Column(Boolean, default=False)


    def __init__(self, *args, **kwargs):
        """initializes Notification"""
        super().__init__(*args, **kwargs)
