#!/usr/bin/env python3
"""Routes to all user restful api actions for Library aid"""

from typing import List
from app.api.routes import api
from flask import jsonify, request, abort, make_response, session
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
    """Create or sign_up a new user"""
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    required_fields = ['email', 'user_name', 'password']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify(
                {"error": f"Missing required field: {field}"}), 400)

    users = storage.all("User").values()
    if any(u.email == data['email'] for u in users):
            return make_response(jsonify(
                {"error": "User already exists"}), 400)

    try:
        new_user = User(**data)
        new_user.save()
        
        storage.save()

        """session['user_id'] = new_user.id
        session['email'] = new_user.email"""

        return jsonify({k: v for k, v in new_user.to_dict().items() if k != 'password'}), 201
    except Exception as e:
            return jsonify({"error whiles creating user": str(e)}), 500
    

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
