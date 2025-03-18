from flask import Blueprint, request, jsonify
from app.services.rating_service import RatingService
from app.utils.auth import token_required
import logging

# Set up logging
logger = logging.getLogger(__name__)

ratings_bp = Blueprint('ratings', __name__)

@ratings_bp.route('', methods=['GET'])
@token_required
def get_ratings(user_id):
    """Get ratings for the current user."""
    logger.info(f"Request to get ratings for user: {user_id}")
    
    # Check if user wants to see ratings they've given or received
    as_rater = request.args.get('as_rater', 'false').lower() == 'true'
    
    # Get ratings
    result = RatingService.get_ratings(user_id, as_rater)
    
    return jsonify(result), 200

@ratings_bp.route('/<rating_id>', methods=['GET'])
@token_required
def get_rating(user_id, rating_id):
    """Get a rating by ID."""
    logger.info(f"Request to get rating: {rating_id}")
    
    # Get rating
    result = RatingService.get_rating_by_id(rating_id, user_id)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify(result), 200

@ratings_bp.route('/submit', methods=['POST'])
@token_required
def submit_rating(user_id):
    """Submit a rating for a trip."""
    logger.info(f"Request to submit rating from user: {user_id}")
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['trip_id', 'rated_user_id', 'rating']
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Validate rating value
    rating_value = data.get('rating')
    if not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
        logger.warning(f"Invalid rating value: {rating_value}")
        return jsonify({'success': False, 'message': 'Rating must be an integer between 1 and 5'}), 400
    
    # Submit rating
    result = RatingService.submit_rating(user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 201

@ratings_bp.route('/user/<user_id>', methods=['GET'])
@token_required
def get_user_ratings(current_user_id, user_id):
    """Get ratings for a specific user."""
    logger.info(f"Request to get ratings for user: {user_id}")
    
    # Get ratings
    result = RatingService.get_user_ratings(user_id)
    
    return jsonify(result), 200

@ratings_bp.route('/trip/<trip_id>', methods=['GET'])
@token_required
def get_trip_ratings(user_id, trip_id):
    """Get ratings for a specific trip."""
    logger.info(f"Request to get ratings for trip: {trip_id}")
    
    # Get ratings
    result = RatingService.get_trip_ratings(trip_id, user_id)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify(result), 200 