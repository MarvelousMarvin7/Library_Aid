#!/usr/bin/env python3
"""Routes to all admin restful api actions for Library aid
helps to balance between normal users and admin users"""

from typing import Union
from app.api.routes import api
from app.api.routes.config import blacklist
from flask import jsonify, Response, request, abort, make_response
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity,\
      create_access_token, create_refresh_token
from flasgger import swag_from
from models import storage
from models.user import User
from models.notification import Notification


@api.route('/admin/signup', methods=['POST'], strict_slashes=False)
@swag_from('documentation/admin/admin_create.yml')
def admin_post_user() -> Union[Response, dict]:
    """Admin: Create or sign_up a new admin user"""
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    required_fields = ['email', 'user_name', 'password', 'is_admin']
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


@api.route('/admin/signin', methods=['POST'], strict_slashes=False)
@swag_from('documentation/admin/admin_signin.yml')
def admin_sign_in() -> Union[Response, dict]:
    """Admin: Sign in admin user"""
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify(
                {"error": f"Missing required field: {field}"}), 400)
    
    data['email'] = data['email'].lower()
    user = storage.get_user_by_email(data['email'])
    if not user or not user.is_admin:
        return make_response(jsonify(
            {"error": "Invalid email or password"}), 401)
    
    if not user.is_valid_password(data['password']):
        return make_response(jsonify(
            {"error": "Invalid email or password"}), 401)
    
    token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "user": {k: v for k, v in user.to_dict().items() if k != 'password'},
        "access_token": token,
        "refresh_token": refresh_token
    }), 200


@api.route('/admin/signout', methods=['POST'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/admin/admin_signout.yml')
def admin_sign_out():
    """Admin: Sign out admin user"""
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Access token revoked"}), 200


@api.route('/admin/users', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/admin/get_all-users.yml')
def get_all_users():
    """Admin: Get all users"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    users = [u.to_dict() for u in storage.all(User).values()]
    return jsonify(users), 200


@api.route('/admin/users/<user_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/admin/get_user_id.yml')
def admin_get_user(user_id: str):
    """Admin: Get user by ID"""
    current_user_id = get_jwt_identity()
    current_user = storage.get(User, current_user_id)
    if not current_user or not current_user.is_admin:
        abort(403, "Admins only")

    user = storage.get(User, user_id)
    if not user:
        abort(404, "User not found")

    return jsonify(user.to_dict()), 200


@api.route('/admin/users/<user_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/admin/update.yml')
def admin_update_user(user_id: str):
    """Admin: Update user by ID"""
    current_user_id = get_jwt_identity()
    current_user = storage.get(User, current_user_id)
    if not current_user or not current_user.is_admin:
        abort(403, "Admins only")

    user = storage.get(User, user_id)
    if not user:
        abort(404, "User not found")

    data = request.get_json(silent=True)
    if not data:
        abort(400, "Not a JSON")

    for key, value in data.items():
        if key not in ['id', 'email', 'created_at', 'updated_at']:
            setattr(user, key, value)

    user.save()
    return jsonify(user.to_dict()), 200


@api.route('/admin/users/<user_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/admin/delete.yml')
def admin_delete_user(user_id: str):
    """Admin: Delete user by ID"""
    current_user_id = get_jwt_identity()
    current_user = storage.get(User, current_user_id)
    if not current_user or not current_user.is_admin:
        abort(403, "Admins only")

    user = storage.get(User, user_id)
    if not user:
        abort(404, "User not found")

    storage.delete(user)
    storage.save()
    return jsonify({}), 200


@api.route('/admin/notifications', methods=['GET'])
@jwt_required()
@swag_from('documentation/admin/get_notif.yml')
def admin_all_notifications() -> Union[Response, dict]:
    """Get Admin notifications"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    notifications = [notification.to_dict() for notification
                     in storage.all(Notification).values()
                     if notification.user_id == user_id]
    return jsonify(notifications), 200


@api.route('/admin/notifications/<notification_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/admin/get_notif_id.yml')
def admin_get_notification(notification_id: str):
    """Admin: Get notification by ID"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    notification = storage.get(Notification, notification_id)
    if not notification:
        abort(404, "Notification not found")

    return jsonify(notification.to_dict()), 200


@api.route('/admin/notifications/<notification_id>',
            methods=['DELETE'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/admin/del_notif_by_id.yml')
def admin_delete_notification(notification_id: str):
    """Admin: Delete notification by ID"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    notification = storage.get(Notification, notification_id)
    if not notification:
        abort(404, "Notification not found")

    storage.delete(notification)
    storage.save()
    return jsonify({}), 200


@api.route('admin/users/<user_id>/notification', methods=['POST'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/admin/create_notif.yml')
def admin_post_notification(user_id: str):
    """Admin: Create a new notification for a user"""
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    required_fields = ['message', 'is_read']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify(
                {"error": f"Missing required field: {field}"}), 400)

    user = storage.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    notification = Notification(**data)
    notification.user_id = user_id
    notification.save()
    return jsonify(notification.to_dict()), 201
