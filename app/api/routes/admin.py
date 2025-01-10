#!/usr/bin/env python3
"""Routes to all admin restful api actions for Library aid
helps to balance between normal users and admin users"""

from typing import List, Union
from app.api.routes import api
from app.api.routes.config import blacklist
from flask import jsonify, Response, request, abort, make_response
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity,\
      create_access_token, create_refresh_token
from models import storage
from models.user import User
from models.document import Document
from models.abstract import Abstract
from models.research import ResearchSession
from models.query import Query
from models.notification import Notification


@api.route('/admin/signup', methods=['POST'], strict_slashes=False)
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
def admin_sign_out():
    """Admin: Sign out admin user"""
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Access token revoked"}), 200


@api.route('/admin/users', methods=['GET'], strict_slashes=False)
@jwt_required()
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


@api.route('/admin/documents', methods=['GET'], strict_slashes=False)
@jwt_required()
def admin_get_documents():
    """Admin: Get all documents"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    documents = [doc.to_dict() for doc in storage.all(Document).values()]
    return jsonify(documents), 200


@api.route('/admin/documents/<document_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def admin_get_document(document_id: str):
    """Admin: Get document by ID"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    document = storage.get(Document, document_id)
    if not document:
        abort(404, "Document not found")

    return jsonify(document.to_dict()), 200


@api.route('/admin/documents/<document_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def admin_delete_document(document_id: str):
    """Admin: Delete document by ID"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    document = storage.get(Document, document_id)
    if not document:
        abort(404, "Document not found")

    storage.delete(document)
    storage.save()
    return jsonify({}), 200


@api.route('/admin/abstracts', methods=['GET'], strict_slashes=False)
@jwt_required()
def admin_get_abstracts():
    """Admin: Get all abstracts"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    abstracts = [abs.to_dict() for abs in storage.all(Abstract).values()]
    return jsonify(abstracts), 200


@api.route('/admin/abstracts/<abstract_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def admin_get_abstract(abstract_id: str):
    """Admin: Get abstract by ID"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    abstract = storage.get(Abstract, abstract_id)
    if not abstract:
        abort(404, "Abstract not found")

    return jsonify(abstract.to_dict()), 200


@api.route('/admin/abstracts/<abstract_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def admin_delete_abstract(abstract_id: str):
    """Admin: Delete abstract by ID"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    abstract = storage.get(Abstract, abstract_id)
    if not abstract:
        abort(404, "Abstract not found")

    storage.delete(abstract)
    storage.save()
    return jsonify({}), 200


@api.route('/admin/notifications', methods=['GET'], strict_slashes=False)
@jwt_required()
def admin_get_notifications():
    """Admin: Get all notifications"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_admin:
        abort(403, "Admins only")

    notifications = [n.to_dict() for n in storage.all(Notification).values()]
    return jsonify(notifications), 200


@api.route('/admin/notifications/<notification_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
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
