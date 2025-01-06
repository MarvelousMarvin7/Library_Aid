#!/usr/bin/python3
"""Main file for implementing api"""

from flask import Flask, make_response
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.api.routes import api
from models import storage
from os import getenv

app = Flask(__name__)
app.register_blueprint(api)
cors = CORS(app, resources={"/*": {"origins": "0.0.0.0"}})


@app.errorhandler(404)
def not_found(error):
    """Error handler for 404"""
    return make_response({"error": "Not found"}, 404)


@app.errorhandler(400)
def bad_request(error):
    """Error handler for 400"""
    return make_response({"error": "Bad request"}, 400)


@app.errorhandler(500)
def internal_error(error):
    """Error handler for 500"""
    return make_response({"error": "Internal server error"}, 500)


@app.teardown_appcontext
def close_session(exception):
    """Closes the session"""
    storage.close()


if __name__ == "__main__":
    """run flask server"""
    host = getenv("LIAID_API_HOST", "0.0.0.0")
    port = int(getenv("LIAID_API_PORT", 5000))
    app.run(host=host, port=port, debug=True)
