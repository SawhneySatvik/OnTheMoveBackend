from flask import Blueprint, request, jsonify
from app.services.vehicle_service import VehicleService
from app.utils.auth import token_required

vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('', methods=['GET'])
@token_required
def get_vehicles(user_id):
    """Get all vehicles for current user."""
    # Get vehicles
    result = VehicleService.get_user_vehicles(user_id)
    
    return jsonify(result), 200

@vehicles_bp.route('/<vehicle_id>', methods=['GET'])
@token_required
def get_vehicle(user_id, vehicle_id):
    """Get a vehicle by ID."""
    # Get vehicle
    result = VehicleService.get_vehicle_by_id(vehicle_id, user_id)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify(result), 200

@vehicles_bp.route('/add', methods=['POST'])
@token_required
def add_vehicle(user_id):
    """Add a new vehicle."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['make', 'model', 'year', 'color', 'license_plate', 'capacity']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    # Add vehicle
    result = VehicleService.add_vehicle(user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 201

@vehicles_bp.route('/<vehicle_id>/update', methods=['PUT'])
@token_required
def update_vehicle(user_id, vehicle_id):
    """Update a vehicle."""
    data = request.get_json()
    
    # Update vehicle
    result = VehicleService.update_vehicle(vehicle_id, user_id, data)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200

@vehicles_bp.route('/<vehicle_id>/delete', methods=['DELETE'])
@token_required
def delete_vehicle(user_id, vehicle_id):
    """Delete a vehicle."""
    # Delete vehicle
    result = VehicleService.delete_vehicle(vehicle_id, user_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result), 200 