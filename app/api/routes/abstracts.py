#!/usr/bin/env python3
"""Routes to all abstract api actions for Library aid
for authorized users
"""

from app.api.routes import api
from flask import jsonify, Response, request, abort, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required
from typing import Union
from models import storage
from models.abstract import Abstract
from models.document import Document
from models.notification import Notification


@api.route('/abstracts', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_abstracts() -> dict:
    """Get all abstracts for a user"""
    user_id = get_jwt_identity()
    abstracts = [abstract.to_dict() for abstract
                 in storage.all(Abstract).values()
                 if abstract.user_id == user_id]
    return jsonify(abstracts), 200


@api.route('/abstracts/<abstract_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_abstract(abstract_id: str) -> dict:
    """Get abstract by id"""
    user_id = get_jwt_identity()
    abstract = storage.get(Abstract, abstract_id)
    if abstract is None or abstract.user_id != user_id:
        abort(404, "Abstract not found or access denied")
    return jsonify(abstract.to_dict())


@api.route('/documents/<document_id>/abstracts', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_document_abstract(document_id: str) -> Union[Response, dict]:
    """Get list of abstract for a document by a user"""
    user_id = get_jwt_identity()
    document = storage.get(Document, document_id)
    if document is None or document.user_id != user_id:
        abort(404, "Document not found or access denied")
    abstracts = [abstract.to_dict() for abstract in document.abstracts]
    return jsonify(abstracts)


@api.route('documents/<document_id>/abstracts', methods=['POST'], strict_slashes=False)
@jwt_required()
def post_abstract(document_id) -> Union[Response, dict]:
    """Create a new abstract for a document
    with abstract complete notification for a user
    """
    user_id = get_jwt_identity()
    document = storage.get(Document, document_id)
    if document is None or document.user_id != user_id:
        abort(404, "Document not found or access denied")
    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")
    if 'abstract_text' not in data:
        abort(400, "Missing required field: abstract_text")
    try:
        data['user_id'] = user_id
        data['document_id'] = document_id
        new_abstract = Abstract(**data)
        new_abstract.save()
        storage.save()
        notification = Notification(
            user_id=user_id,
            message=f"Abstract for {document.title} created")
        notification.save()
        return make_response(jsonify(new_abstract.to_dict()), 201)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/abstracts/<abstract_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def put_abstract(abstract_id: str) -> Union[Response, dict]:
    """Update an abstract by id"""
    user_id = get_jwt_identity()
    abstract = storage.get(Abstract, abstract_id)
    if abstract is None or abstract.user_id != user_id:
        abort(404, "Abstract not found or access denied")
    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")
    for key, value in data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(abstract, key, value)
    abstract.save()
    return make_response(jsonify(abstract.to_dict()), 200)


@api.route('/abstracts/<abstract_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_abstract(abstract_id: str) -> Union[Response, dict]:
    """Delete an abstract by id with user access and notification"""
    user_id = get_jwt_identity()
    abstract = storage.get(Abstract, abstract_id)
    if abstract is None or abstract.user_id != user_id:
        abort(404, "Abstract not found or access denied")
    try:
        storage.delete(abstract)
        storage.save()
        notification = Notification(
            user_id=user_id,
            message=f"Abstract deleted")
        notification.save()
        return make_response(jsonify({}), 200)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

