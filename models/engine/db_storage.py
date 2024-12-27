#!/usr/bin/env python3
"""Database storage"""

from os import getenv
from typing import Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base, BaseModel
from models.user import User
from models.document import Document
from models.query import Query
from models.tag import Tag
from models.research import ResearchSession
from models.abstract import Abstract
from models.notification import Notification
from models.classification import Classification


classes = {'BaseModel': BaseModel, 'User': User, 'Document': Document,
           'Query': Query, 'Tag': Tag, 'ResearchSession': ResearchSession,
           'Abstract': Abstract, 'Notification': Notification,
           'Classification': Classification}


class DB_storage():
    """Mysql database storage"""
    __engine = None
    __session = None

    def __init__(self):
        """Instantiate a DBStorage object"""
        LIAID_MYSQL_USER = getenv('LIAID_MYSQL_USER')
        LIAID_MYSQL_PWD = getenv('LIAID_MYSQL_PWD')
        LIAID_MYSQL_HOST = getenv('LIAID_MYSQL_HOST')
        LIAID_MYSQL_DB = getenv('LIAID_MYSQL_DB')
        LIAID_ENV = getenv('LIAID_ENV')
        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.
                                      format(LIAID_MYSQL_USER,
                                             LIAID_MYSQL_PWD,
                                             LIAID_MYSQL_HOST,
                                             LIAID_MYSQL_DB))
        if LIAID_ENV == "test":
            Base.metadata.drop_all(self.__engine)
    
    def all(self, cls=None) -> Dict:
        """query on the current database session"""
        new_dict = {}
        for clss in classes:
            if cls is None or cls is classes[clss] or cls is clss:
                objs = self.__session.query(classes[clss]).all()
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    new_dict[key] = obj
        return (new_dict)

    def new(self, obj):
        """add the object to the current database session"""
        self.__session.add(obj)

    def save(self):
        """commit all changes of the current database session"""
        self.__session.commit()

    def delete(self, obj=None):
        """delete from the current database session obj if not None"""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """reloads data from the database"""
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session
