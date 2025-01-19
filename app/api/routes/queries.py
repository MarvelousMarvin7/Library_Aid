#!/usr/bin/env python3
"""Routes to all queries api actions for Library aid"""

from typing import Union
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.routes import api
from flask import jsonify, request, Response
from models import storage
from models.query import Query
from models.research import ResearchSession


@api.route('/sessions/<session_id>/query', methods=['POST'], strict_slashes=False)
@jwt_required()
def query_session(session_id: str) -> Union[Response, dict]:
    """Handle user queries for a specific active research session."""
    user_id = get_jwt_identity()
    session = storage.get(ResearchSession, session_id)

    if not session or session.user_id != user_id:
        return jsonify({"error": "Session not found or unauthorized"}), 404

    if session.session_end is not None:
        return jsonify({"error": "Cannot query a session that has ended"}), 400

    data = request.get_json()
    if not data or 'query_text' not in data:
        return jsonify({"error": "Missing query_text"}), 400

    try:
        data['user_id'] = user_id
        data['research_session_id'] = session_id
        query = Query(**data)
        query.save()
        storage.save()

        return jsonify({
            "query_id": query.id,
            "query_text": query.query_text,
            "response_text": query.response_text,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/sessions/<session_id>/query', methods=['GET'],
 strict_slashes=False)
@jwt_required()
def get_session_queries(session_id: str) -> Union[Response, dict]:
    """Get all queries for a specific active research session."""
    user_id = get_jwt_identity()
    session = storage.get(ResearchSession, session_id)

    if not session or session.user_id != user_id:
        return jsonify({"error": "Session not found or unauthorized"}), 404

    queries = [query.to_dict() for query in session.queries]
    return jsonify(queries), 200
