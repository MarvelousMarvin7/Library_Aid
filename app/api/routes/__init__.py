#!/usr/bin/env python3
"""Blueprint for api"""

from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

from app.api.routes.index import *
from app.api.routes.admin import *
from app.api.routes.users import *
from app.api.routes.documents import *
from app.api.routes.abstracts import *
from app.api.routes.notifications import *
from app.api.routes.queries import *
from app.api.routes.researches import *
