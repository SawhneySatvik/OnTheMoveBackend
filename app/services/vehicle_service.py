from datetime import datetime
from app.utils.supabase_client import supabase, supabase_admin
from app.models.vehicle import Vehicle
import logging

# Set up logging
logger = logging.getLogger(__name__)

class VehicleService:
    """Service for handling vehicle operations."""
    
    @staticmethod
    def get_user_vehicles(user_id):
        """Get all vehicles for a user."""
        try:
            logger.info(f"Getting vehicles for user: {user_id}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('vehicles').select('*').eq('user_id', user_id).execute()
            
            vehicles = [Vehicle.from_dict(vehicle).to_dict() for vehicle in response.data]
            logger.info(f"Found {len(vehicles)} vehicles for user: {user_id}")
            
            return {
                'success': True,
                'vehicles': vehicles
            }
            
        except Exception as e:
            logger.error(f"Error getting vehicles: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_vehicle_by_id(vehicle_id, user_id=None):
        """Get a vehicle by ID."""
        try:
            logger.info(f"Getting vehicle by ID: {vehicle_id}, user_id: {user_id}")
            
            # Use supabase_admin to bypass RLS policies
            query = supabase_admin.table('vehicles').select('*').eq('id', vehicle_id)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.execute()
            
            if not response.data:
                logger.info(f"Vehicle not found: {vehicle_id}")
                return {'success': False, 'message': 'Vehicle not found'}
            
            vehicle = Vehicle.from_dict(response.data[0])
            logger.info(f"Found vehicle: {vehicle_id}")
            
            return {
                'success': True,
                'vehicle': vehicle.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting vehicle: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def add_vehicle(user_id, data):
        """Add a new vehicle."""
        try:
            logger.info(f"Adding vehicle for user: {user_id}")
            
            # Create vehicle
            vehicle_data = {
                'user_id': user_id,
                'make': data.get('make'),
                'model': data.get('model'),
                'year': data.get('year'),
                'color': data.get('color'),
                'license_plate': data.get('license_plate'),
                'capacity': data.get('capacity'),
                'image_url': data.get('image_url'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('vehicles').insert(vehicle_data).execute()
            
            if not response.data:
                logger.error("Failed to add vehicle")
                return {'success': False, 'message': 'Failed to add vehicle'}
            
            vehicle = Vehicle.from_dict(response.data[0])
            logger.info(f"Vehicle added successfully: {vehicle.id}")
            
            return {
                'success': True,
                'vehicle': vehicle.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error adding vehicle: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_vehicle(vehicle_id, user_id, data):
        """Update a vehicle."""
        try:
            logger.info(f"Updating vehicle: {vehicle_id} for user: {user_id}")
            
            # Check if vehicle exists and belongs to user
            response = supabase_admin.table('vehicles').select('*').eq('id', vehicle_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.info(f"Vehicle not found or does not belong to user: {vehicle_id}")
                return {'success': False, 'message': 'Vehicle not found or does not belong to user'}
            
            # Update vehicle
            update_data = {k: v for k, v in data.items() if k in [
                'make', 'model', 'year', 'color', 'license_plate', 'capacity', 'image_url'
            ]}
            
            update_data['updated_at'] = datetime.utcnow().isoformat()
            logger.info(f"Updating vehicle fields: {', '.join(update_data.keys())}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('vehicles').update(update_data).eq('id', vehicle_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.error("Failed to update vehicle")
                return {'success': False, 'message': 'Failed to update vehicle'}
            
            vehicle = Vehicle.from_dict(response.data[0])
            logger.info(f"Vehicle updated successfully: {vehicle_id}")
            
            return {
                'success': True,
                'vehicle': vehicle.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error updating vehicle: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def delete_vehicle(vehicle_id, user_id):
        """Delete a vehicle."""
        try:
            logger.info(f"Deleting vehicle: {vehicle_id} for user: {user_id}")
            
            # Check if vehicle exists and belongs to user
            response = supabase_admin.table('vehicles').select('*').eq('id', vehicle_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.info(f"Vehicle not found or does not belong to user: {vehicle_id}")
                return {'success': False, 'message': 'Vehicle not found or does not belong to user'}
            
            # Delete vehicle
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('vehicles').delete().eq('id', vehicle_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.error("Failed to delete vehicle")
                return {'success': False, 'message': 'Failed to delete vehicle'}
            
            logger.info(f"Vehicle deleted successfully: {vehicle_id}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error deleting vehicle: {str(e)}")
            return {'success': False, 'message': str(e)} 