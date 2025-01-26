#!/usr/bin/python3
"""Main file for implementing api"""

from flask import Flask, make_response
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from app.api.routes import api
from app.api.routes.config import blacklist
from models import storage
from os import getenv

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Library Aid API',
    'uiversion': 3,
    'openapi': '3.0.2',
    'components': {
        'securitySchemes': {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
    'security': [{'bearerAuth': []}],
    'info': {
        'version': '1.0',
        'title': 'Library Aid API',
        'description': 'A web application to help manage library resources',
        'contact': {
            'name': 'Marvin Agyei',
            'email': 'marvinagyei3@gmail.com',
            'url': 'https://github.com/MarvelousMarvin7/Library_Aid'
        },
    },
    'specs': [
        {
            'endpoint': 'apispec_1',
            'route': '/apispec_1.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'servers': [
        {
            'url': 'http://127.0.0.1:5000',
            'description': 'Localhost server'
        }
    ],
}
swagger = Swagger(app)
app.config["JWT_SECRET_KEY"] = getenv("LIAID_JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
app.config["JWT_ALGORITHM"] = "HS256"
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    """Check if a token is in the blacklist"""
    jti = jwt_payload['jti']
    return jti in blacklist

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
