from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.auth import token_required
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Register user
    result = AuthService.register(
        email=data['email'],
        password=data['password'],
        name=data['name'],
        phone=data.get('phone'),
        date_of_birth=data.get('date_of_birth'),
        gender=data.get('gender'),
        institute=data.get('institute')
    )
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Login user
    result = AuthService.login(
        email=data['email'],
        password=data['password']
    )
    
    if not result['success']:
        return jsonify(result), 401
    
    return jsonify(result), 200

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh an access token."""
    logger = logging.getLogger(__name__)
    
    data = request.get_json()
    logger.info("Received refresh token request")
    
    # Validate required fields
    if 'refresh_token' not in data:
        logger.warning("Missing refresh_token field in request")
        return jsonify({'success': False, 'message': 'Missing required field: refresh_token'}), 400
    
    # Refresh token
    logger.info("Calling AuthService.refresh_token")
    result = AuthService.refresh_token(data['refresh_token'])
    
    if not result['success']:
        logger.warning(f"Token refresh failed: {result['message']}")
        return jsonify(result), 401
    
    logger.info("Token refreshed successfully")
    return jsonify(result), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout a user."""
    data = request.get_json()
    
    # Validate required fields
    if 'refresh_token' not in data:
        return jsonify({'success': False, 'message': 'Missing required field: refresh_token'}), 400
    
    # Logout user
    result = AuthService.logout(data['refresh_token'])
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(user_id):
    """Get current user profile."""
    from app.services.user_service import UserService
    
    # Get user
    result = UserService.get_user_by_id(user_id)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify(result), 200 