from flask import Blueprint, request, jsonify
from app.services.person_service import PersonService
from app.utils.auth import token_required
import logging

# Set up logging
logger = logging.getLogger(__name__)

people_bp = Blueprint('people', __name__)

@people_bp.route('', methods=['GET'])
@token_required
def get_people(user_id):
    """Get all people for current user."""
    logger.info(f"Request to get all people for user: {user_id}")
    
    # Get people
    result = PersonService.get_user_people(user_id)
    
    return jsonify(result), 200

@people_bp.route('/<person_id>', methods=['GET'])
@token_required
def get_person(user_id, person_id):
    """Get a person by ID."""
    logger.info(f"Request to get person: {person_id} for user: {user_id}")
    
    # Get person
    result = PersonService.get_person_by_id(person_id, user_id)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify(result), 200

@people_bp.route('/add', methods=['POST'])
@token_required
def add_person(user_id):
    """Add a new person."""
    logger.info(f"Request to add person for user: {user_id}")
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Add person
    result = PersonService.add_person(user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 201

@people_bp.route('/<person_id>/update', methods=['PUT'])
@token_required
def update_person(user_id, person_id):
    """Update a person."""
    logger.info(f"Request to update person: {person_id} for user: {user_id}")
    data = request.get_json()
    
    # Update person
    result = PersonService.update_person(person_id, user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@people_bp.route('/<person_id>/delete', methods=['DELETE'])
@token_required
def delete_person(user_id, person_id):
    """Delete a person."""
    logger.info(f"Request to delete person: {person_id} for user: {user_id}")
    
    # Delete person
    result = PersonService.delete_person(person_id, user_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@people_bp.route('/<person_id>/favorite', methods=['PUT'])
@token_required
def toggle_favorite(user_id, person_id):
    """Toggle the favorite status of a person."""
    logger.info(f"Request to toggle favorite status for person: {person_id}, user: {user_id}")
    
    # Toggle favorite status
    result = PersonService.toggle_favorite(person_id, user_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200 