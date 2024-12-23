#!/usr/bin/python3
""" holds class Product"""
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, ForeignKey, String, Float
from sqlalchemy.orm import relationship


class Product(BaseModel, Base):
    """Representation of Product """
    __tablename__ = 'products'
    user_id = Column(String(60), ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    titile = Column(String(128), nullable=False)
    description = Column(String(1024), nullable=False)
    path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    image_url = Column(String(128), nullable=True)
    orders = relationship("Order", backref="product", cascade="all, delete")

    def __init__(self, *args, **kwargs):
        """initializes Product"""
        super().__init__(*args, **kwargs)
