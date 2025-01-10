#!/usr/bin/env python3
"""Routes to all document restful api actions for Library aid
authorized users 
"""

from typing import List, Union

from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.routes import api
from flask import jsonify, request, abort, make_response, Response
from models import storage
from models.document import Document


@api.route('/documents', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_documents() -> dict:
    """Get all documents for a user"""
    user_id = get_jwt_identity()
    documents = [document.to_dict() for document
                  in storage.all(Document).values()
                 if document.user_id == user_id]
    return jsonify(documents), 200


@api.route('/documents/<document_id>', methods=['GET'],
            strict_slashes=False)
@jwt_required()
def get_document(document_id: str) -> dict:
    """Get document by id"""
    user_id = get_jwt_identity()
    document = storage.get(Document, document_id)
    if document is None or document.user_id != user_id:
        abort(404, "Document not found or access denied")
    return jsonify(document.to_dict())


@api.route('/documents/search/title', methods=['GET'], strict_slashes=False)
@jwt_required()
def search_documents_by_title() -> List:
    """Search documents by title"""
    user_id = get_jwt_identity()
    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Missing title parameter"}), 400

    try:
        documents = storage.search_by_title(Document, title)
        user_documents = [doc.to_dict() for doc in documents
                           if doc.user_id == user_id]
        return jsonify(user_documents)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/documents/search/classification_code',
            methods=['GET'], strict_slashes=False)
@jwt_required()
def search_documents_by_classification_code() -> dict:
    """Search documents by classification code"""
    user_id = get_jwt_identity()
    code = request.args.get('classification_code')
    if not code:
        return jsonify({"error": "Missing classification_code parameter"}), 400

    try:
        documents = storage.search_by_classification_code(Document, code)
        user_documents = [doc.to_dict() for doc in documents if doc.user_id == user_id]
        return jsonify(user_documents)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/documents', methods=['POST'], strict_slashes=False)
@jwt_required()
def post_document() -> dict:
    """Create a new document"""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Not a JSON"}), 400

    required_fields = ['title', 'file_path', 'file_type']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    if data['file_type'] not in ['PDF', 'TXT', 'JPEG', 'DOCX', 'PNG']:
        return jsonify({"error": "Invalid file_type"}), 400

    try:
        data['user_id'] = user_id
        document = Document(**data)
        document.save()
        storage.save()
        return jsonify(document.to_dict()), 201
    except Exception as e:
        return jsonify({"error while creating document": str(e)}), 500


@api.route('/documents/<document_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def put_document(document_id: str) -> Union[Response, dict]:
    """Update document by id"""
    user_id = get_jwt_identity()
    document = storage.get(Document, document_id)
    if document is None or document.user_id != user_id:
        abort(404, "Document not found or access denied")

    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")

    for key, value in data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(document, key, value)

    document.save()
    return make_response(jsonify(document.to_dict()), 200)


@api.route('/documents/<document_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_document(document_id: str) -> Union[Response, dict]:
    """Delete document by id"""
    user_id = get_jwt_identity()
    document = storage.get(Document, document_id)
    if document is None or document.user_id != user_id:
        abort(404, "Document not found or access denied")

    storage.delete(document)
    storage.save()
    return make_response(jsonify({}), 200)
