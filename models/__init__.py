#!/usr/bin/env python3
"""
initialize the models package
"""

from os import getenv


storage_t = getenv("LIAID_TYPE_STORAGE")
from models.engine.db_storage import DB_storage

storage = DB_storage()
storage.reload()