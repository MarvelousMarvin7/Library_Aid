#!/usr/bin/env python3
""""Routes to all notification api actions for Library aid"""

from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.routes import api
from flask import jsonify, Response, abort, make_response
from flasgger import swag_from
from typing import Union
from models import storage
from models.notification import Notification


@api.route('/notifications', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/notification/get_all.yml')
def get_user_notifications() -> Union[Response, dict]:
    """Get list of all notifications for
    the current user"""
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "User not found"}), 404

    notifications = [notification.to_dict() for notification
                     in storage.all(Notification).values()
                     if notification.user_id == user_id]
    return jsonify(notifications), 200


@api.route('/notifications/<notification_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/notification/get_by_id.yml')
def get_notification(notification_id: str) -> Union[Response, dict]:
    """Get notification by id for a user"""
    user_id = get_jwt_identity()
    notification = storage.get(Notification, notification_id)
    if notification is None or notification.user_id != user_id:
        abort(404, "Notification not found or access denied")
    return jsonify(notification.to_dict())


@api.route('/notifications/<notification_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/notification/delete.yml')
def delete_notification(notification_id: str) -> Union[Response, dict]:
    """Delete notification by id"""
    user_id = get_jwt_identity()
    notification = storage.get(Notification, notification_id)
    if notification is None or notification.user_id != user_id:
        abort(404, "Notification not found or access denied")
    storage.delete(notification)
    storage.save()
    return jsonify({}), 200


@api.route('/notifications/<notification_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
@swag_from('documentation/notification/mark_read.yml')
def mark_notification_as_read(notification_id: str) -> Response:
    """Current user update notifications as read"""
    user_id = get_jwt_identity()
    notification = storage.get(Notification, notification_id)
    if notification is None or notification.user_id != user_id:
        abort(404, "Notification not found or access denied")
    notification.is_read = True
    notification.save()
    return make_response(jsonify(notification.to_dict()), 200)
