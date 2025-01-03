#!/usr/bin/env python3
"""index of Api"""

from app.api.routes import api
from flask import jsonify

@api.route('/status', methods=['GET'])
def status() -> str:
    """Return status"""
    return jsonify({"status": "OK"})
