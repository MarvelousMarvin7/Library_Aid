#!/usr/bin/env python3
"""Database storage"""

from os import getenv
from typing import Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import List, Any
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

    def search_by_title(self, cls, title: str) -> List[Any]:
        """Search for objects of a specific class by title."""
        if cls not in classes.values():
            raise ValueError("Invalid class provided for search.")
        return self.__session.query(cls).filter(cls.title.ilike(f"%{title}%"))
    
    def search_by_classification_code(self, cls, code: str) -> Any:
        """Search for objects of a specific class by classification code
        or category code for institutional users."""
        if cls not in classes.values():
            raise ValueError("Invalid class provided for search.")
        if hasattr(cls, 'classification_code'):
            return self.__session.query(cls).filter(cls.classification_code.ilike(f"%{code}%"))
        elif hasattr(cls, 'category_code'):
            return self.__session.query(cls).filter(cls.category_code.ilike(f"%{code}%"))
        else:
            raise AttributeError(f"The class {cls.__name__}\
                                  does not have classification_code or\
                                  category_code.")

    def check_file_exists(self, cls, file_path: str) -> bool:
        """Check if a file exists in the database."""
        if cls not in classes.values():
            raise ValueError("Invalid class provided for search.")
        return self.__session.query(cls).filter(cls.file_path == file_path).count() > 0

    def filter_first(self, cls, **filters):
        """Filter a model by a set of parameters and return the first result."""
        return self.__session.query(cls).filter_by(**filters).first()

    def get_user_sessions(self, user_id: str) -> List[ResearchSession]:
        """Fetch all research sessions for a user."""
        return self.__session.query(ResearchSession).filter_by(user_id=user_id).all()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch user by email"""
        return self.__session.query(User).filter_by(email=email).first()

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

    def close(self):
        """close the current database session"""
        self.__session.remove()

    def get(self, cls, id):
        """get an object based on the class and its ID"""
        if cls is None or id is None:
            return None
        obj = self.__session.query(cls).filter_by(id=id).first()
        return obj

    def reload(self):
        """reloads data from the database"""
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session
