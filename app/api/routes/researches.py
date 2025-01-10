#!/usr/bin/env python3
"""Routes to all research restful api actions for Library aid"""

import datetime
from typing import Union
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.routes import api
from flask import jsonify, request, abort, make_response, Response
from models import storage
from models.research import ResearchSession
from models.user import User
from models.document import Document


@api.route('/research_sessions', methods=['GET'], strict_slashes=False)
@jwt_required()
def start_or_get_session() -> Union[Response, dict]:
    """Get active research session or start a new one"""
    user_id = get_jwt_identity()
    
    research_sessions = [
        session for session in storage.all(ResearchSession).values()
        if session.user_id == user_id
    ]

    active_session = next(
        (session for session in research_sessions
          if session.session_end is None),
        None
    )

    if not active_session:
        new_session = ResearchSession(
            user_id=user_id,
            session_start=datetime.utcnow()
        )
        new_session.save()
        storage.save()
        return jsonify({"message": "New session started",
                         "session": new_session.to_dict()}), 201

    return jsonify({"message": "Active session found",
                     "session": active_session.to_dict()}), 200


@api.route('/research_sessions/<research_session_id>',
            methods=['GET'], strict_slashes=False)
@jwt_required()
def get_research(research_session_id: str) -> dict:
    """Get research by id"""
    research = storage.get(ResearchSession, research_session_id)
    if research is None:
        abort(404)
    return jsonify(research.to_dict())


@api.route('/users/<user_id>/research_sessions',
 methods=['GET'], strict_slashes=False)
@jwt_required()
def get_user_researches(user_id: str) -> Union[Response, dict]:
    """Get list of all research_sessions for a user"""
    list_of_researches = []
    user = storage.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    for research in user.research_sessions:
        list_of_researches.append(research.to_dict())
    return make_response(jsonify(list_of_researches), 200)


@api.route('/documents/<document_id>/research_sessions',
 methods=['GET'], strict_slashes=False)
@jwt_required()
def get_document_researches(document_id: str) -> Union[Response, dict]:
    """Get list of research_sessions for a document"""
    list_of_researches = []
    document = storage.get(Document, document_id)
    if document is None:
        abort(404)
    for research in document.research_sessions:
        list_of_researches.append(research.to_dict())
    return make_response(jsonify(list_of_researches), 200) 


@api.route('/research_sessions/<research_session_id>/documents',
 methods=['GET'], strict_slashes=False)
@jwt_required()
def get_research_documents(research_session_id: str) -> Union[Response, dict]:
    """Get list of documents for a research_session"""
    list_of_documents = []
    research = storage.get(ResearchSession, research_session_id)
    if research is None:
        abort(404)
    for document in research.documents:
        list_of_documents.append(document.to_dict())
    return make_response(jsonify(list_of_documents), 200)


@api.route('/research_sessions', methods=['POST'], strict_slashes=False)
@jwt_required()
def post_research() -> Union[Response, dict]:
    """Create a new research session"""
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    required_fields = ['user_id', 'session_tile']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify(
                {"error": f"Missing required field: {field}"}), 400)

    user = storage.get(User, data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    research = ResearchSession(
        user_id = data['user_id'],
        session_title = data['session_title']
    )
    research.save()
    return make_response(jsonify(research.to_dict()), 200)


@api.route('/users/<user_id>/research_sessions/title/<session_title>',
            methods=['GET'], strict_slashes=False)
def get_user_research_by_title(user_id: str, session_title: str) -> Union[Response, dict]:
    """Get list of research sessions by title for a user"""
    list_of_researches = []
    user = storage.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    for research in user.research_sessions:
        if research.session_title == session_title:
            list_of_researches.append(research.to_dict())
    if not list_of_researches:
        return jsonify({"error": "No research session found"}), 404
    return make_response(jsonify(list_of_researches), 200)


@api.route('/research_sessions/<research_session_id>/documents',
 methods = ['POST'], strict_slashes=False)
@jwt_required()
def post_document_to_research(research_session_id: str) -> Union[Response, dict]:
    """Add a document to a research session"""
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    required_fields = ['document_id']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify(   
                {"error": f"Missing required field: {field}"}), 400)

    research = storage.get(ResearchSession, research_session_id)
    if not research:
        return jsonify({"error": "Research session not found"}), 404

    document = storage.get(Document, data['document_id'])
    if not document:
        return jsonify({"error": "Document not found"}), 404

    if document in research.documents:
        return jsonify({"error": "Document already in research session"}), 400

    research.documents.append(document)
    storage.save()
    return make_response(jsonify(document.to_dict()), 200)


@api.route('/research_sessions/<research_session_id>/close',
            methods=['PUT'], strict_slashes=False)
@jwt_required()
def close_research_session(research_session_id: str) -> Union[Response, dict]:
    """Close an active research session"""
    research = storage.get(ResearchSession, research_session_id)
    if not research or research.session_end:
        return jsonify({"error": "No active session found"}), 404

    research.session_end = datetime.utcnow()
    research.save()
    return jsonify({"message": "Session closed",
                     "session": research.to_dict()}), 200


@api.route('/research_sessions/<research_session_id>/documents',
            methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_document_from_research(research_session_id:
                                   str) -> Union[Response, dict]:
    """Delete a document from a research session"""
    data = request.get_json(silent=True)
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    required_fields = ['document_id']
    for field in required_fields:
        if field not in data:
            return make_response(jsonify(
                {"error": f"Missing required field: {field}"}), 400)

    research = storage.get(ResearchSession, research_session_id)
    if not research:
        return jsonify({"error": "Research session not found"}), 404

    document = storage.get(Document, data['document_id'])
    if not document:
        return jsonify({"error": "Document not found"}), 404

    if document not in research.documents:
        return jsonify({"error": "Document not in research session"}), 400

    research.documents.remove(document)
    storage.save()
    return make_response(jsonify({}), 200)


@api.route('/research_sessions/<research_session_id>',
            methods=['PUT'], strict_slashes=False)
@jwt_required()
def put_research(research_session_id: str) -> Union[Response, dict]:
    """Update research session by id"""
    research = storage.get(ResearchSession, research_session_id)
    if research is None:
        abort(404)
    data = request.get_json(silent=True)
    if data is None:
        abort(400, "Not a JSON")
    for key, value in data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(research, key, value)
    research.save()
    return make_response(jsonify(research.to_dict()), 200)


@api.route('/research_sessions/<research_session_id>',
 methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_research(research_session_id: str) -> Union[Response, dict]:
    """Delete research session by id"""
    research = storage.get(ResearchSession, research_session_id)
    if research is None:
        abort(404)
    storage.delete(research)
    storage.save()
    return make_response(jsonify({}), 200)
