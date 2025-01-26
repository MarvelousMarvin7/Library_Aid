#!/usr/bin/env python3
"""Routes to all user restful api actions for Library aid"""

import os
from typing import Union
from app.api.routes import api
from app.api.routes.config import blacklist
from flask import jsonify, Response, request, abort, make_response
from flask_jwt_extended import create_access_token, create_refresh_token,\
      get_jwt, jwt_required, get_jwt_identity
from flasgger import swag_from
from models import storage
from models.user import User


@api.route('/signup', methods=['POST'], strict_slashes=False)
@swag_from('documentation/user/user_signup.yml')
def post_user() -> Union[Response, dict]:
    """Create or sign_up a new user"""
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    required_fields = ['email', 'user_name', 'password']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify(
                {"error": f"Missing required field: {field}"}), 400)

    data['email'] = data['email'].lower()
    users = storage.all("User").values()
    if any(u.email == data['email'] for u in users):
            return make_response(jsonify(
                {"error": "User already exists"}), 400)
    
    try:
        new_user = User(**data)
        new_user.save()
        storage.save()

        token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)

        return jsonify({
            "user": {k: v for k, v in new_user.to_dict().items()
         if k != 'password'},
            "access_token": token,
            "refresh_token": refresh_token
         }), 201
    except Exception as e:
            return jsonify({"error whiles creating user": str(e)}), 500


@api.route('/signin', methods=['POST'], strict_slashes=False)
@swag_from('documentation/user/user_signin.yml')
def sign_in() -> Union[Response, dict]:
    """Sign in user"""
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify(
                {"error": f"Missing required field: {field}"}), 400)

    data['email'] = data['email'].lower()
    try:
        user = storage.get_user_by_email(data['email'])
        if user is None or not user.is_valid_password(data['password']):
            return make_response(jsonify({"error": "Invalid credentials"}), 401)

        token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            "user": {k: v for k, v in user.to_dict().items() if k != 'password'},
            "access_token": token,
            "refresh_token": refresh_token
        }), 200

    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred while signing in"}
            ), 500


@api.route('/signout', methods=['POST'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/user/user_signout.yml')
def signout():
    """Logout user by blacklisting their token"""
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200


@api.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/user/user_update.yml')
def put_user(user_id: str) -> Union[Response, dict]:
    """Update user by id"""
    if user_id != get_jwt_identity():
        abort(403, "Access denied")

    user = storage.get(User, user_id)
    if user is None:
        abort(404, "User not found")

    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")

    for key, value in data.items():
        if key not in ['id', 'email', 'created_at', 'updated_at']:
            setattr(user, key, value)

    user.save()
    storage.save()

    return make_response(jsonify(user.to_dict()), 200)


@api.route('/users/<user_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/user/user_delete.yml')
def delete_user(user_id: str) -> Union[Response, dict]:
    """Delete user by id"""
    if user_id != get_jwt_identity():
        abort(403, "Access denied")

    user = storage.get(User, user_id)
    if user is None:
        abort(404, "User not found")

    storage.delete(user)
    storage.save()

    return make_response(jsonify({}), 200)
