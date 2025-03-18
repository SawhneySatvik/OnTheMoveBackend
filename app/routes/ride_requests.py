from flask import Blueprint, request, jsonify
from app.services.ride_request_service import RideRequestService
from app.utils.auth import token_required
import logging

# Set up logging
logger = logging.getLogger(__name__)

ride_requests_bp = Blueprint('ride_requests', __name__)

@ride_requests_bp.route('', methods=['GET'])
@token_required
def get_ride_requests(user_id):
    """Get all ride requests for a user."""
    logger.info(f"Request to get ride requests for user: {user_id}")
    
    # Check if user wants to see requests as a driver
    is_driver = request.args.get('is_driver', 'false').lower() == 'true'
    
    # Get ride requests
    result = RideRequestService.get_ride_requests(user_id, is_driver)
    
    return jsonify(result), 200

@ride_requests_bp.route('/pending/<trip_id>', methods=['GET'])
@token_required
def get_pending_ride_requests(user_id, trip_id):
    """Get pending ride requests for a trip."""
    logger.info(f"Request to get pending ride requests for trip: {trip_id}, user: {user_id}")
    
    result = RideRequestService.get_pending_requests_for_trip(trip_id, user_id)
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@ride_requests_bp.route('/<request_id>', methods=['GET'])
@token_required
def get_ride_request(user_id, request_id):
    """Get a ride request by ID."""
    logger.info(f"Request to get ride request: {request_id} for user: {user_id}")
    
    # Get ride request
    result = RideRequestService.get_ride_request_by_id(request_id, user_id)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify(result), 200

@ride_requests_bp.route('/create', methods=['POST'])
@token_required
def create_ride_request(user_id):
    """Create a new ride request."""
    logger.info(f"Request to create ride request for user: {user_id}")
    data = request.get_json()
    
    # Validate required fields
    required_fields = [
        'trip_id', 
        'pickup_latitude', 'pickup_longitude', 'pickup_address',
        'dropoff_latitude', 'dropoff_longitude', 'dropoff_address',
        'seats_requested'
    ]
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Create ride request
    result = RideRequestService.create_ride_request(user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 201



@ride_requests_bp.route('/<request_id>/accept', methods=['PUT'])
@token_required
def accept_ride_request(user_id, request_id):
    """Accept a ride request (driver only)."""
    logger.info(f"Request to accept ride request: {request_id} by driver: {user_id}")
    
    # Accept ride request
    result = RideRequestService.update_ride_request_status(request_id, user_id, 'accepted', is_driver=True)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@ride_requests_bp.route('/<request_id>/reject', methods=['PUT'])
@token_required
def reject_ride_request(user_id, request_id):
    """Reject a ride request (driver only)."""
    logger.info(f"Request to reject ride request: {request_id} by driver: {user_id}")
    
    # Reject ride request
    result = RideRequestService.update_ride_request_status(request_id, user_id, 'rejected', is_driver=True)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@ride_requests_bp.route('/<request_id>/cancel', methods=['PUT'])
@token_required
def cancel_ride_request(user_id, request_id):
    """Cancel a ride request (passenger only)."""
    logger.info(f"Request to cancel ride request: {request_id} by passenger: {user_id}")
    
    # Cancel ride request
    result = RideRequestService.update_ride_request_status(request_id, user_id, 'cancelled', is_driver=False)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200 
