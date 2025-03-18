from flask import Blueprint, request, jsonify
from app.services.location_service import LocationService
from app.utils.auth import token_required
import logging

# Set up logging
logger = logging.getLogger(__name__)

locations_bp = Blueprint('locations', __name__)

@locations_bp.route('', methods=['GET'])
@token_required
def get_locations(user_id):
    """Get all locations for current user."""
    logger.info(f"Request to get all locations for user: {user_id}")
    
    # Get locations
    result = LocationService.get_user_locations(user_id)
    
    return jsonify(result), 200

@locations_bp.route('/<location_id>', methods=['GET'])
@token_required
def get_location(user_id, location_id):
    """Get a location by ID."""
    logger.info(f"Request to get location: {location_id} for user: {user_id}")
    
    # Get location
    result = LocationService.get_location_by_id(location_id, user_id)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify(result), 200

@locations_bp.route('/add', methods=['POST'])
@token_required
def add_location(user_id):
    """Add a new location."""
    logger.info(f"Request to add location for user: {user_id}")
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'address', 'latitude', 'longitude']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Add location
    result = LocationService.add_location(user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 201

@locations_bp.route('/<location_id>/update', methods=['PUT'])
@token_required
def update_location(user_id, location_id):
    """Update a location."""
    logger.info(f"Request to update location: {location_id} for user: {user_id}")
    data = request.get_json()
    
    # Update location
    result = LocationService.update_location(location_id, user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@locations_bp.route('/<location_id>/delete', methods=['DELETE'])
@token_required
def delete_location(user_id, location_id):
    """Delete a location."""
    logger.info(f"Request to delete location: {location_id} for user: {user_id}")
    
    # Delete location
    result = LocationService.delete_location(location_id, user_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@locations_bp.route('/<location_id>/favorite', methods=['PUT'])
@token_required
def toggle_favorite(user_id, location_id):
    """Toggle the favorite status of a location."""
    logger.info(f"Request to toggle favorite status for location: {location_id}, user: {user_id}")
    
    # Toggle favorite status
    result = LocationService.toggle_favorite(location_id, user_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200 