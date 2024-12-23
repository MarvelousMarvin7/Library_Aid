#!/usr/bin/env python3
"""Database storage"""

from os import getenv
import sqlalchemy
from sqlalchemy import create_session
from sqlalchemy.orm import sessionmaker, scoped_session


class DB_storage():
    """Mysql database storage"""
    __engine = None
    __session = None

    def __init__(self):
        """Instantiate a DBStorage object"""
        LIAID_MYSQL_USER = getenv('LIAID_MYSQL_USER')
        LIAID_MYSQL_PWD = getenv('LIAI_MYSQL_PWD')
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
