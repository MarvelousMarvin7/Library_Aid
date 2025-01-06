#!/usr/bin/env python3
"""Routes to all document restful api actions for Library aid"""

from typing import List, Union
from app.api.routes import api
from flask import jsonify, request, abort, make_response, Response
from models import storage
from models.document import Document

@api.route('/documents', methods=['GET'], strict_slashes=False)
def get_documents() -> dict:
    """Get all documents"""
    documents = storage.all(Document).values()
    documents = [document.to_dict() for document in documents]
    return jsonify(documents)


@api.route('/documents/<document_id>', methods=['GET'], strict_slashes=False)
def get_document(document_id: str) -> dict:
    """Get document by id"""
    document = storage.get(Document, document_id)
    if document is None:
        abort(404)
    return jsonify(document.to_dict())


@api.route('/documents/search/title', methods=['GET'], strict_slashes=False)
def search_documents_by_title() -> List:
    """Search documents by title"""
    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Missing title parameter"}), 400

    try:
        documents = storage.search_by_title(Document, title)
        if not documents:
            return jsonify([])
        return jsonify([document.to_dict() for document in documents])
    except ValueError as e:
        return jsonify({"error":str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/documents/search/classification_code',
 methods=['GET'], strict_slashes=False)
def search_documents_by_classification_code() -> dict:
    """Search documents by classification code"""
    code = request.args.get('classification_code')
    if not code:
        return jsonify({"error": "Missing classification_code parameter"}), 400

    try:
        documents = storage.search_by_classification_code(Document, code)
        if not documents:
            return jsonify([])
        return jsonify([document.to_dict() for document in documents])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/documents', methods=['POST'], strict_slashes=False)
def post_document() -> dict:
    """Create a new document"""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Not a JSON"}), 400

    required_fields = ['user_id', 'title', 'file_path', 'file_type']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    if data['file_type'] not in ['PDF', 'TXT', 'JPEG', 'DOCX', 'PNG']:
        return jsonify({"error": "Invalid file_type"}), 400

    try:
        document = Document(**data)
        document.save()

        storage.save()

        return jsonify(document.to_dict()), 201
    except Exception as e:
        return jsonify({"error whiles creating document": str(e)}), 500


@api.route('/documents/<document_id>', methods=['PUT'], strict_slashes=False)
def put_document(document_id: str) -> Union[Response, dict]:
    """Update document by id"""
    document = storage.get(Document, document_id)
    if document is None:
        abort(404)
    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")
    for key, value in data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(document, key, value)
    document.save()
    return make_response(jsonify(document.to_dict()), 200)


@api.route('/documents/<document_id>', methods=['DELETE'], strict_slashes=False)
def delete_document(document_id: str) -> Union[Response, dict]:
    """Delete document by id"""
    document = storage.get(Document, document_id)
    if document is None:
        abort(404)
    storage.delete(document)
    storage.save()
    return make_response(jsonify({}), 200)
