#!/usr/bin/env python3
""""Routes to all notification api actions for Library aid"""

from app.api.routes import api
from flask import jsonify, Response, request, abort, make_response
from typing import Union
from models import storage
from models.notification import Notification
from models.user import User


@api.route('/notifications', methods=['GET'], strict_slashes=False)
def get_notifications() -> dict:
    """Get all notifications"""
    notifications = storage.all(Notification).values()
    notifications = [notification.to_dict() for notification in notifications]
    return jsonify(notifications)


@api.route('/users/<user_id>/notifications', methods=['GET'], strict_slashes=False)
def get_user_notifications(user_id: str) -> Union[Response, dict]:
    """Get list of all notifications for a user"""
    list_of_notifications = []
    user = storage.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    for notification in user.notifications:
        list_of_notifications.append(notification.to_dict())
    return make_response(jsonify(list_of_notifications), 200)


@api.route('/notifications/<notification_id>', methods=['GET'], strict_slashes=False)
def get_notification(notification_id: str) -> Union[Response, dict]:
    """Get notification by id"""
    notification = storage.get(Notification, notification_id)
    if notification is None:
        abort(404)
    return make_response(jsonify(notification.to_dict()), 200)


@api.route('/notifications/<notification_id>', methods=['DELETE'], strict_slashes=False)
def delete_notification(notification_id: str) -> Union[Response, dict]:
    """Delete notification by id"""
    notification = storage.get(Notification, notification_id)
    if notification is None:
        abort(404)
    storage.delete(notification)
    storage.save()
    return make_response(jsonify({}), 200)


@api.route('/users/<user_id>/notification', methods=['POST'], strict_slashes=False)
def post_notification(user_id: str) -> Union[Response, dict]:
    """Create a new notification for a user"""
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
    storage.save()
    return make_response(jsonify(notification.to_dict()), 201)


@api.route('/notifications/<notification_id>', methods=['PUT'], strict_slashes=False)
def mark_notification_as_read(notification_id: str) -> Response:
    """Update notification as read"""
    notification = storage.get(Notification, notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    
    notification.is_read = True
    notification.save()
    storage.save()
    return make_response(jsonify(notification.to_dict()), 200)
