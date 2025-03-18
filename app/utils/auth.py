import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.config import get_config
import logging

# Set up logging
logger = logging.getLogger(__name__)

config = get_config()

def generate_access_token(user_id):
    """Generate a JWT access token."""
    payload = {
        'sub': str(user_id),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    logger.info(f"Generating access token for user: {user_id}")
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm='HS256')

def generate_refresh_token(user_id):
    """Generate a JWT refresh token."""
    payload = {
        'sub': str(user_id),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=config.JWT_REFRESH_TOKEN_EXPIRES)
    }
    logger.info(f"Generating refresh token for user: {user_id}")
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """Decode a JWT token."""
    try:
        logger.info(f"Decoding token: {token[:10]}...")
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        logger.info(f"Token decoded successfully for user: {payload['sub']}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None

def token_required(f):
    """Decorator to require a valid JWT token for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            logger.info(f"Found token in Authorization header: {token[:10]}...")
        
        if not token:
            logger.warning("No token found in request")
            return jsonify({'error': 'Unauthorized', 'message': 'Token is missing'}), 401
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            logger.warning("Token validation failed")
            return jsonify({'error': 'Unauthorized', 'message': 'Token is invalid or expired'}), 401
        
        # Add user_id to kwargs
        kwargs['user_id'] = payload['sub']
        logger.info(f"Token validated for user: {payload['sub']}")
        
        return f(*args, **kwargs)
    
    return decorated 