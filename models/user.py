#!/usr/bin/python3
""" holds class User"""
import bcrypt
from models.base_model import BaseModel, Base
from sqlalchemy import BOOLEAN, Column, String
from sqlalchemy.orm import relationship


class User(BaseModel, Base):
    """Representation of a user """
    __tablename__ = 'users'
    email = Column(String(128), nullable=False)
    password = Column(String(60), nullable=False)
    user_name = Column(String(128), nullable=False)
    image_url = Column(String(128), nullable=True)
    is_institution_user = Column(BOOLEAN, nullable=True, default=False)
    documents = relationship("Document", backref="user")
    research_sessions = relationship("ResearchSession", backref="user")
    queries = relationship("Query", backref="user")
    notifications = relationship("Notification", backref="user")

    def __init__(self, *args, **kwargs):
        """initializes user"""
        if 'password' in kwargs:
            kwargs['password'] = self.hash_password(kwargs['password'])
        super().__init__(*args, **kwargs)

    def hash_password(self, password):
        """hashes password"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def is_valid_password(self, password):
        """checks if password is valid"""
        return bcrypt.checkpw(
                password.encode('utf-8'), self.password.encode('utf-8')
            )
