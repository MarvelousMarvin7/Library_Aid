#!/usr/bin/env python3
"""Blueprint for api"""

from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

from app.api.routes.index import *
from app.api.routes.users import *
from app.api.routes.documents import *
