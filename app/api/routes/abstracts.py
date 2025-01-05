#!/usr/bin/env python3
"""Routes to all abstract api actions for Library aid"""

from app.api.routes import api
from flask import jsonify, Response, request, abort, make_response
from typing import Union
from models import storage
from models.abstract import Abstract
from models.document import Document
from models.notification import Notification


@api.route('/abstracts', methods=['GET'], strict_slashes=False)
def get_abstracts() -> dict:
    """Get all abstracts"""
    abstracts = storage.all(Abstract).values()
    abstracts = [abstract.to_dict() for abstract in abstracts]
    return jsonify(abstracts)


@api.route('/abstracts/<abstract_id>', methods=['GET'], strict_slashes=False)
def get_abstract(abstract_id: str) -> dict:
    """Get abstract by id"""
    abstract = storage.get(Abstract, abstract_id)
    if abstract is None:
        abort(404)
    return jsonify(abstract.to_dict())


@api.route('/documents/<document_id>/abstracts', methods=['GET'], strict_slashes=False)
def get_document_abstract(document_id: str) -> Union[Response, dict]:
    """Get list of abstract for a document"""
    list_abstracts = []
    document = storage.get(Document, document_id)
    if document is None:
        abort(404)
    for abstract in document.abstracts:
        list_abstracts.append(abstract.to_dict())
    return make_response(jsonify(list_abstracts), 200)


@api.route('documents/<document_id>/abstracts', methods=['POST'], strict_slashes=False)
def post_abstract(document_id) -> Union[Response, dict]:
    """Create a new abstract for a document
    with abstract complete notification
    """
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    required_fields = ['document_id', 'abstract_text']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify(
                {"error": f"Missing required field: {field}"}), 400)
    
    document = storage.get(Document, document_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404
    
    try:
        abstract = Abstract(**data)
        abstract.save()

        # Create the notification
        notification = Notification(
            user_id=document.user_id,
            message="Your abstract has been successfully created!"
        )
        notification.save()
            
        storage.save()

        return jsonify(abstract.to_dict()), 201
    except Exception as e:
            return jsonify({"error whiles creating abstract": str(e)}), 500


@api.route('/abstracts/<abstract_id>', methods=['PUT'], strict_slashes=False)
def put_abstract(abstract_id: str) -> Union[Response, dict]:
    """Update abstract by id"""
    abstract = storage.get(Abstract, abstract_id)
    if abstract is None:
        abort(404)
    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")
    for key, value in data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(abstract, key, value)
    abstract.save()
    return make_response(jsonify(abstract.to_dict()))


@api.route('/abstracts/<abstract_id>', methods=['DELETE'], strict_slashes=False)
def delete_abstract(abstract_id: str) -> Union[Response, dict]:
    """Delete an abstract by id"""
    abstract = storage.get(Abstract, abstract_id)
    if abstract is None:
        abort(404)
    storage.delete(abstract)
    storage.save()
    return make_response(jsonify({}), 200)
