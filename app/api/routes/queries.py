#!/usr/bin/env python3
"""Routes to all queries api actions for Library aid"""

from typing import Union
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.routes import api
from flask import jsonify, request, abort, make_response, Response
from models import storage
from models.query import Query
from models.document import Document
from models.user import User
from models.research import ResearchSession


@api.route('/queries', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_queries() -> dict:
    """Get all queries"""
    queries = storage.all(Query).values()
    queries = [query.to_dict() for query in queries]
    return jsonify(queries)


@api.route('/queries/<query_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_query(query_id: str) -> dict:
    """Get query by id"""
    query = storage.get(Query, query_id)
    if query is None:
        abort(404)
    return jsonify(query.to_dict())


@api.route('/users/<user_id>/queries', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_user_queries(user_id: str) -> Union[Response, dict]:
    """Get list of all queries for a user"""
    list_of_queries = []
    user = storage.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    for query in user.queries:
        list_of_queries.append(query.to_dict())
    return make_response(jsonify(list_of_queries), 200)


@api.route('/research_sessions/<research_session_id>/queries',
            methods=['GET'], strict_slashes=False)
@jwt_required()
def get_research_session_queries(research_session_id: str) -> Union[Response, dict]:
    """Get list of queries for a research session"""
    list_of_queries = []
    research_session = storage.get(ResearchSession, research_session_id)
    if research_session is None:
        abort(404)
    for query in research_session.queries:
        list_of_queries.append(query.to_dict())
    return make_response(jsonify(list_of_queries), 200)


@api.route('/queries', methods=['POST'], strict_slashes=False)
@jwt_required()
def post_query() -> Union[Response, dict]:
    """Create a new query for the current user"""
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    # Get the current user ID from the JWT
    user_id = get_jwt_identity()

    required_fields = ['research_session_id', 'query_text']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify(
                {"error": f"Missing required field: {field}"}), 400)

    research_session = storage.get(ResearchSession, data['research_session_id'])
    if not research_session or research_session.user_id != user_id:
        return jsonify({"error": "Research session not found or access denied"}), 404

    document_id = data.get('document_id')
    if document_id:
        document = storage.get(Document, document_id)
        if not document or document not in research_session.documents:
            return jsonify({"error": "Document not found or not part of the research session"}), 404

    query = Query(
        user_id=user_id,
        research_session_id=data['research_session_id'],
        query_text=data['query_text'],
        document_id=document_id
    )
    query.save()
    storage.save()
    return make_response(jsonify(query.to_dict()), 200)


@api.route('/queries/<query_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_query(query_id: str) -> Union[Response, dict]:
    """Delete query by id"""
    query = storage.get(Query, query_id)
    if query is None:
        abort(404)
    storage.delete(query)
    storage.save()
    return make_response(jsonify({}), 200)


@api.route('/queries/<query_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def put_query(query_id: str) -> Union[Response, dict]:
    """Update query by id"""
    query = storage.get(Query, query_id)
    if query is None:
        abort(404)
    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")
    for key, value in data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(query, key, value)
    query.save()
    return make_response(jsonify(query.to_dict()), 200)
