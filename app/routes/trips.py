from flask import Blueprint, request, jsonify
from app.services.trip_service import TripService
from app.utils.auth import token_required
import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

trips_bp = Blueprint('trips', __name__)

@trips_bp.route('', methods=['GET'])
@token_required
def get_trips(user_id):
    """Get all trips with optional filters."""
    logger.info(f"Request to get trips for user: {user_id}")
    
    # Get query parameters
    filters = {}
    
    # Check if user wants to see their own trips as a driver
    is_driver = request.args.get('is_driver', 'false').lower() == 'true'
    if is_driver:
        filters['driver_id'] = user_id
    
    # Add other filters
    if 'status' in request.args:
        filters['status'] = request.args.get('status')
    if 'start_time_after' in request.args:
        filters['start_time_after'] = request.args.get('start_time_after')
    if 'start_time_before' in request.args:
        filters['start_time_before'] = request.args.get('start_time_before')
    
    # Get trips
    result = TripService.get_trips(filters)
    
    return jsonify(result), 200

@trips_bp.route('/upcoming', methods=['GET'])
@token_required
def get_upcoming_trips(user_id):
    """Get upcoming trips for the authenticated user."""
    logger.info(f"Request to get upcoming trips for user: {user_id}")
    
    role = request.args.get('role', 'both')  # 'driver', 'passenger', or 'both'
    
    result = TripService.get_upcoming_trips(user_id, role)
    if not result['success']:
        return jsonify(result), 500  # Use 500 for server errors
    
    return jsonify(result), 200

@trips_bp.route('/search/enriched', methods=['GET'])
@token_required
def search_enriched_trips(user_id):
    """Search for trips with enriched data."""
    logger.info(f"Request to search enriched trips for user: {user_id}")
    
    filters = {
        'status': 'scheduled',
        'start_time_after': request.args.get('start_time_after', datetime.datetime.now().isoformat()),
        'near_latitude': request.args.get('near_latitude'),
        'near_longitude': request.args.get('near_longitude'),
        'radius_km': request.args.get('radius_km', '10'),  # Default 10 km
        'min_available_seats': request.args.get('min_available_seats'),
        'max_price': request.args.get('max_price')
    }
    
    result = TripService.search_enriched_trips(user_id, filters)
    if not result['success']:
        return jsonify(result), 500  # Use 500 for server errors
    
    return jsonify(result), 200

@trips_bp.route('/<trip_id>', methods=['GET'])
@token_required
def get_trip(user_id, trip_id):
    """Get a trip by ID."""
    logger.info(f"Request to get trip: {trip_id}")
    
    # Get trip
    result = TripService.get_trip_by_id(trip_id)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify(result), 200

@trips_bp.route('/create', methods=['POST'])
@token_required
def create_trip(user_id):
    """Create a new trip."""
    logger.info(f"Request to create trip for user: {user_id}")
    data = request.get_json()
    
    # Validate required fields
    required_fields = [
        'vehicle_id', 
        'start_latitude', 'start_longitude', 'start_address',
        'end_latitude', 'end_longitude', 'end_address',
        'start_time', 'available_seats', 'price'
    ]
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Create trip
    result = TripService.create_trip(user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 201

@trips_bp.route('/<trip_id>/update', methods=['PUT'])
@token_required
def update_trip(user_id, trip_id):
    """Update a trip."""
    logger.info(f"Request to update trip: {trip_id} for user: {user_id}")
    data = request.get_json()
    
    # Update trip
    result = TripService.update_trip(trip_id, user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@trips_bp.route('/<trip_id>/cancel', methods=['PUT'])
@token_required
def cancel_trip(user_id, trip_id):
    """Cancel a trip."""
    logger.info(f"Request to cancel trip: {trip_id} for user: {user_id}")
    
    # Cancel trip
    result = TripService.cancel_trip(trip_id, user_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@trips_bp.route('/<trip_id>/start', methods=['PUT'])
@token_required
def start_trip(user_id, trip_id):
    """Start a trip."""
    logger.info(f"Request to start trip: {trip_id} for user: {user_id}")
    
    # Start trip
    result = TripService.start_trip(trip_id, user_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@trips_bp.route('/<trip_id>/complete', methods=['PUT'])
@token_required
def complete_trip(user_id, trip_id):
    """Complete a trip."""
    logger.info(f"Request to complete trip: {trip_id} for user: {user_id}")
    
    # Complete trip
    result = TripService.complete_trip(trip_id, user_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@trips_bp.route('/search', methods=['GET'])
@token_required
def search_trips(user_id):
    """Search for trips based on filters."""
    logger.info(f"Request to search trips from user: {user_id}")
    
    # Get query parameters
    filters = {}
    
    # Add filters
    if 'status' in request.args:
        filters['status'] = request.args.get('status')
    if 'start_time_after' in request.args:
        filters['start_time_after'] = request.args.get('start_time_after')
    if 'start_time_before' in request.args:
        filters['start_time_before'] = request.args.get('start_time_before')
    if 'min_available_seats' in request.args:
        filters['min_available_seats'] = int(request.args.get('min_available_seats'))
    if 'max_price' in request.args:
        filters['max_price'] = float(request.args.get('max_price'))
    
    # Add coordinate-based search parameters
    if all(key in request.args for key in ['near_latitude', 'near_longitude']):
        filters['near_latitude'] = request.args.get('near_latitude')
        filters['near_longitude'] = request.args.get('near_longitude')
        filters['radius_km'] = request.args.get('radius_km', '1')  # Default radius is 1 km
    
    # Search trips
    result = TripService.search_trips(filters)
    
    return jsonify(result), 200

@trips_bp.route('/stats', methods=['GET'])
@token_required
def get_trip_stats(user_id):
    """Get trip statistics for the current user."""
    logger.info(f"Request to get trip statistics for user: {user_id}")
    
    # Get trip statistics
    result = TripService.get_trip_stats(user_id)
    
    return jsonify(result), 200

@trips_bp.route('/history', methods=['GET'])
@token_required
def get_trip_history(user_id):
    """Get trip history for the current user."""
    logger.info(f"Request to get trip history for user: {user_id}")
    
    # Get query parameters
    filters = {}
    
    # Add filters
    if 'role' in request.args:
        filters['role'] = request.args.get('role')  # 'driver', 'passenger', or both if not specified
    if 'status' in request.args:
        filters['status'] = request.args.get('status')
    if 'from_date' in request.args:
        filters['from_date'] = request.args.get('from_date')
    if 'to_date' in request.args:
        filters['to_date'] = request.args.get('to_date')
    
    # Pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    filters['page'] = page
    filters['limit'] = limit
    
    # Get trip history
    result = TripService.get_trip_history(user_id, filters)
    
    return jsonify(result), 200

@trips_bp.route('/<trip_id>/participants', methods=['GET'])
@token_required
def get_trip_participants(user_id, trip_id):
    """Get participants (driver and passengers) for a trip."""
    logger.info(f"Request to get participants for trip: {trip_id}")
    
    # Get trip participants
    result = TripService.get_trip_participants(trip_id, user_id)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify(result), 200 
