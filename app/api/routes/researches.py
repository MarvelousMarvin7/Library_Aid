#!/usr/bin/env python3
"""Routes to all research restful api actions for Library aid"""

from datetime import datetime
from typing import Union
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.routes import api
from flask import jsonify, request, Response
from models import storage
from models.research import ResearchSession, SessionDocuments
from models.document import Document


@api.route('/sessions', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_session():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'session_title' not in data or 'document_ids' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        session = ResearchSession(
            user_id=user_id,
            session_title=data['session_title'],
            session_start=datetime.utcnow(),
            session_end=None
        )
        session.save()

        accessed_documents = []
        for doc_id in data['document_ids']:
            document = storage.get(Document, doc_id)
            if document and document.user_id == user_id:
                session_doc = SessionDocuments(
                    research_session_id=session.id,
                    document_id=doc_id
                )
                storage.new(session_doc)
                accessed_documents.append({
                    "id": document.id,
                    "title": document.title,
                    "created_at": document.created_at
                })
        storage.save()

        response = session.to_dict()
        response["documents_accessed"] = accessed_documents
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/sessions', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_sessions() -> Union[Response, dict]:
    """
    Fetch all research sessions for the logged-in user.
    Optionally include filters via query parameters.
    """
    user_id = get_jwt_identity()
    active_only = request.args.get('active', 'false').lower() == 'true'
    sessions = storage.get_user_sessions(user_id)

    if active_only:
        sessions = [session for session in sessions if not session.session_end]

    session_list = [
        {
            "id": session.id,
            "session_title": session.session_title,
            "session_start": session.session_start.isoformat(),
            "session_end": session.session_end.isoformat()\
                  if session.session_end else None,
            "active": session.session_end is None,
        }
        for session in sessions
    ]

    return jsonify(session_list), 200


@api.route('/sessions/<session_id>/end', methods=['PATCH'], strict_slashes=False)
@jwt_required()
def end_session(session_id: str) -> Union[Response, dict]:
    """End a research session."""
    user_id = get_jwt_identity()
    session = storage.get(ResearchSession, session_id)

    if not session or session.user_id != user_id:
        return jsonify({"error": "Session not found or unauthorized"}), 404

    session.session_end = datetime.utcnow()
    session.save()
    storage.save()
    return jsonify(session.to_dict()), 200


@api.route('/sessions/<session_id>', methods=['DELETE'],
            strict_slashes=False)
@jwt_required()
def delete_session(session_id: str) -> Union[Response, dict]:
    """Delete a research session."""
    user_id = get_jwt_identity()
    session = storage.get(ResearchSession, session_id)

    if not session or session.user_id != user_id:
        return jsonify({"error": "Session not found or unauthorized"}), 404

    storage.delete(session)
    storage.save()
    return jsonify({}), 200
