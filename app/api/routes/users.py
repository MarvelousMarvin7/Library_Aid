#!/usr/bin/env python3
"""Routes to all user restful api actions for Library aid"""

from typing import List
from app.api.routes import api
from flask import jsonify, request, abort, make_response
from models import storage
from models.user import User

@api.route('/users', methods=['GET'], strict_slashes=False)
def get_users() -> List:
    """Get all users"""
    users = storage.all(User).values()
    users = [user.to_dict() for user in users]
    return jsonify(users)


@api.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
def get_user(user_id: str) -> User:
    """Get user by id"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    return jsonify(user.to_dict())


@api.route('/users', methods=['POST'], strict_slashes=False)
def post_user() -> User:
    """Create a new user"""
    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")
    if "email" not in data:
        abort(400, "Missing email")
    if "password" not in data:
        abort(400, "Missing password")
    user = User(**data)
    user.save()
    return make_response(jsonify(user.to_dict()), 201)


@api.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
def put_user(user_id: str) -> User:
    """Update user by id"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")
    for key, value in data.items():
        if key not in ['id', 'email', 'created_at', 'updated_at']:
            setattr(user, key, value)
    user.save()
    return make_response(jsonify(user.to_dict()), 200)


@api.route('/users/<user_id>', methods=['DELETE'], strict_slashes=False)
def delete_user(user_id: str) -> str:
    """Delete user by id"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    storage.delete(user)
    storage.save()
    return make_response(jsonify({}), 200)
