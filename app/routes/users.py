from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from app.utils.auth import token_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get a user by ID."""
    # Get user
    result = UserService.get_user_by_id(user_id)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify(result), 200

@users_bp.route('/me', methods=['PUT'])
@token_required
def update_me(user_id):
    """Update current user profile."""
    data = request.get_json()
    
    # Update user
    result = UserService.update_user(user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@users_bp.route('/complete-onboarding', methods=['PUT'])
@token_required
def complete_onboarding(user_id):
    """Mark onboarding as completed for current user."""
    # Complete onboarding
    result = UserService.complete_onboarding(user_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200 