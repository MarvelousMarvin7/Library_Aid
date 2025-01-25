#!/usr/bin/env python3
"""Routes to all tags api actions for Library aid"""

from app.api.routes import api
from typing import Union
from flask import jsonify, Response, request, abort
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


@api.route('/documents/<document_id>/tags',
            methods=['POST'], strict_slashes=False)
@jwt_required()
def post_document_tag(document_id: str) -> Union[Response, dict]:
    """Associate a predefined enum tag with a document"""
    user_id = get_jwt_identity()
    document = storage.get(Document, document_id)
    if document is None or document.user_id != user_id:
        return jsonify({"error": "Document not found or access denied"}), 404

    data = request.get_json(silent=True)
    if data is None or 'tag_name' not in data:
        return jsonify({"error": "Not a JSON or missing tag_name"}), 400

    predefined_tags = ['AI', 'Important', 'Art', 'Science', 'Mathematics',
                       'My Document', 'History', 'Archaeology', 'Physics',
                       'Economics', 'Chemistry', 'Research', 'Technology']

    tag_name = data['tag_name']
    if tag_name not in predefined_tags:
        return jsonify({"error": f"Invalid tag name: {tag_name}"}), 400

    try:
        if tag_name not in [tag.tag for tag in document.tags]:
            tag = Tag(tag=tag_name)
            document.tags.append(tag)
            storage.save()

        return jsonify({"message": f"Tag '\
                        {tag_name}' associated with document"}), 201
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
    if tag is None or tag not in document.tags:
        abort(404, "Tag not found or unauthorized")

    try:
        document.tags.remove(tag)
        storage.save()
        return jsonify({"message": "Tag removed successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
