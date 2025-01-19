#!/usr/bin/env python3
"""Routes to all tags api actions for Library aid"""

from app.api.routes import api
from typing import Union
from flask import jsonify, Response, request, abort, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required
from typing import Union
from models import storage
from models.document import Document
from models.tag import Tag


@api.route('/documents/<document_id>/tags', methods=['GET'],
            strict_slashes=False)
@jwt_required()
def get_document_tags(document_id: str) -> Union[Response, dict]:
    """Get list of tags for a document by a user"""
    user_id = get_jwt_identity()
    document = storage.get(Document, document_id)
    if document is None or document.user_id != user_id:
        abort(404, "Document not found or access denied")
    tags = [tag.to_dict() for tag in document.tags]
    return jsonify(tags), 200


@api.route('/documents/<document_id>/tags', methods=['PUT'],
            strict_slashes=False)
@jwt_required()
def update_document_tags(document_id: str) -> Union[Response, dict]:
    """Update tags for a document"""
    user_id = get_jwt_identity()
    document = storage.get(Document, document_id)

    if document is None or document.user_id != user_id:
        abort(404, "Document not found or access denied")

    data = request.get_json(silent=True)
    if data is None or 'tag_ids' not in data:
        return jsonify({"error": "Not a JSON or missing tag_ids"}), 400

    try:
        document.tags.clear()

        for tag_id in data['tag_ids']:
            tag = storage.get(Tag, tag_id)
            if tag and tag.user_id == user_id:
                document.tags.append(tag)
            else:
                return jsonify({"error": f"Invalid or \
                                unauthorized tag ID: {tag_id}"}), 400

        storage.save()
        return jsonify({"message": "Tags updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/documents/<document_id>/tags/<tag_id>',
            methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_document_tag(document_id: str,
                         tag_id: str) -> Union[Response, dict]:
    """Delete a specific tag from a document"""
    user_id = get_jwt_identity()
    document = storage.get(Document, document_id)

    if document is None or document.user_id != user_id:
        abort(404, "Document not found or access denied")

    tag = storage.get(Tag, tag_id)
    if tag is None or tag.user_id != user_id or tag not in document.tags:
        abort(404, "Tag not found or unauthorized")

    try:
        document.tags.remove(tag)
        storage.save()
        return jsonify({"message": "Tag removed successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
