#!/usr/bin/env python3
"""Routes to all classification api actions for Library aid"""

from app.api.routes import api
from typing import Union
from flask import jsonify, Response, request, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from typing import Union
from models import storage
from models.document import Document
from models.classification import Classification
from models.user import User


@api.route('/classifications', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_classifications() -> Union[Response, dict]:
    """Get all classifications"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_institution_user:
        abort(403, "Only institutional users can access classifications")

    classifications = []
    for classification in storage.all(Classification).values():
        classification_data = classification.to_dict()
        if classification.documents:
            classification_data["document_name"] = classification.documents[0].title
        classifications.append(classification_data)
    
    return jsonify(classifications), 200


@api.route('/classifications/<classification_id>',
            methods=['GET'], strict_slashes=False)
@jwt_required()
def get_classification(classification_id: str):
    """Get a classification by ID"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_institution_user:
        abort(403, "Only institutional users can access classifications")

    classification = storage.get(Classification, classification_id)
    if not classification:
        abort(404, "Classification not found")
    
    classification_data =  classification.to_dict()
    if classification.documents:
        classification_data["document_name"] = classification.documents[0].title
        classification_data["document_image"] = classification.documents[0].image_url
    
    return jsonify(classification_data), 200


@api.route('/classifications/search/category_code', methods=['GET'], strict_slashes=False)
@jwt_required()
def search_documents_by_category_code() -> dict:
    """Search documents by classification's category
      code (institutional users only)"""
    user_id = get_jwt_identity()

    user = storage.get(User, user_id)
    if not user or not user.is_institution_user:
        abort(403, "Only institutional users are allowed to search by category code")

    category_code = request.args.get('category_code')
    if not category_code:
        return jsonify({"error": "Missing category_code parameter"}), 400

    try:
        classifications = storage.search_by_classification_code(Classification, category_code)
        if not classifications:
            return jsonify({"error": "Classification not found"}), 404

        classification_data_list = []
        for classification in classifications:
            classification_data = classification.to_dict()
            if classification.documents:
                classification_data["document_name"] = classification.documents[0].title
                classification_data["document_image"] = classification.documents[0].image_url
            classification_data_list.append(classification_data)

        return jsonify(classification_data_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@api.route('/classify', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_classification() -> Union[Response, dict]:
    """Create a new classification"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_institution_user:
        abort(403, "Only institutional users can create classifications")

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Not a JSON"}), 400

    required_fields = ['name', 'category_code', 'description']
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing fields: {', '.join(required_fields)}"}), 400

    document = storage.get(Document, data['document_id'])
    if not document or document.user_id != user_id:
        abort(404, "Document not found or access denied")
    
    if document.classification_id:
        return jsonify({"error": "Document is already classified"}), 400

    try:
        classification = Classification(
            name=data['name'],
            category_code=data['category_code'],
            description=data['description'],
            parent_id=data.get('parent_id')
        )
        classification.save()
        document.classification_id = classification.id
        storage.save()
        response = {
            "classification": classification.to_dict(),
            "document": {
                "id": document.id,
                "title": document.title,
                "classification_id": document.classification_id,
                "classification_code": classification.category_code,
            }
        }
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/classifications/<classification_id>',
            methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_classification(classification_id: str):
    """Delete a classification"""
    user_id = get_jwt_identity()
    user = storage.get(User, user_id)
    if not user or not user.is_institution_user:
        abort(403, "Only institutional users can delete classifications")

    classification = storage.get(Classification, classification_id)
    if not classification:
        abort(404, "Classification not found")

    classification.delete()
    storage.save()
    return jsonify({}), 200
