from datetime import datetime
from app.utils.supabase_client import supabase, supabase_admin
from app.models.location import Location
import logging

# Set up logging
logger = logging.getLogger(__name__)

class LocationService:
    """Service for handling location operations."""
    
    @staticmethod
    def get_user_locations(user_id):
        """Get all locations for a user."""
        try:
            logger.info(f"Getting locations for user: {user_id}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('locations').select('*').eq('user_id', user_id).execute()
            
            locations = [Location.from_dict(location).to_dict() for location in response.data]
            logger.info(f"Found {len(locations)} locations for user: {user_id}")
            
            return {
                'success': True,
                'locations': locations
            }
            
        except Exception as e:
            logger.error(f"Error getting locations: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_location_by_id(location_id, user_id=None):
        """Get a location by ID."""
        try:
            logger.info(f"Getting location by ID: {location_id}, user_id: {user_id}")
            
            # Use supabase_admin to bypass RLS policies
            query = supabase_admin.table('locations').select('*').eq('id', location_id)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.execute()
            
            if not response.data:
                logger.info(f"Location not found: {location_id}")
                return {'success': False, 'message': 'Location not found'}
            
            location = Location.from_dict(response.data[0])
            logger.info(f"Found location: {location_id}")
            
            return {
                'success': True,
                'location': location.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting location: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def add_location(user_id, data):
        """Add a new location."""
        try:
            logger.info(f"Adding location for user: {user_id}")
            
            # Create location
            location_data = {
                'user_id': user_id,
                'name': data.get('name'),
                'address': data.get('address'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'is_favorite': data.get('is_favorite', False),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('locations').insert(location_data).execute()
            
            if not response.data:
                logger.error("Failed to add location")
                return {'success': False, 'message': 'Failed to add location'}
            
            location = Location.from_dict(response.data[0])
            logger.info(f"Location added successfully: {location.id}")
            
            return {
                'success': True,
                'location': location.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error adding location: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_location(location_id, user_id, data):
        """Update a location."""
        try:
            logger.info(f"Updating location: {location_id} for user: {user_id}")
            
            # Check if location exists and belongs to user
            response = supabase_admin.table('locations').select('*').eq('id', location_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.info(f"Location not found or does not belong to user: {location_id}")
                return {'success': False, 'message': 'Location not found or does not belong to user'}
            
            # Update location
            update_data = {k: v for k, v in data.items() if k in [
                'name', 'address', 'latitude', 'longitude', 'is_favorite'
            ]}
            
            update_data['updated_at'] = datetime.utcnow().isoformat()
            logger.info(f"Updating location fields: {', '.join(update_data.keys())}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('locations').update(update_data).eq('id', location_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.error("Failed to update location")
                return {'success': False, 'message': 'Failed to update location'}
            
            location = Location.from_dict(response.data[0])
            logger.info(f"Location updated successfully: {location_id}")
            
            return {
                'success': True,
                'location': location.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error updating location: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def delete_location(location_id, user_id):
        """Delete a location."""
        try:
            logger.info(f"Deleting location: {location_id} for user: {user_id}")
            
            # Check if location exists and belongs to user
            response = supabase_admin.table('locations').select('*').eq('id', location_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.info(f"Location not found or does not belong to user: {location_id}")
                return {'success': False, 'message': 'Location not found or does not belong to user'}
            
            # Delete location
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('locations').delete().eq('id', location_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.error("Failed to delete location")
                return {'success': False, 'message': 'Failed to delete location'}
            
            logger.info(f"Location deleted successfully: {location_id}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error deleting location: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def toggle_favorite(location_id, user_id):
        """Toggle the favorite status of a location."""
        try:
            logger.info(f"Toggling favorite status for location: {location_id}, user: {user_id}")
            
            # Check if location exists and belongs to user
            response = supabase_admin.table('locations').select('*').eq('id', location_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.info(f"Location not found or does not belong to user: {location_id}")
                return {'success': False, 'message': 'Location not found or does not belong to user'}
            
            # Get current favorite status
            current_location = Location.from_dict(response.data[0])
            new_favorite_status = not current_location.is_favorite
            
            # Update favorite status
            update_data = {
                'is_favorite': new_favorite_status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('locations').update(update_data).eq('id', location_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.error("Failed to update favorite status")
                return {'success': False, 'message': 'Failed to update favorite status'}
            
            location = Location.from_dict(response.data[0])
            logger.info(f"Favorite status toggled to {location.is_favorite} for location: {location_id}")
            
            return {
                'success': True,
                'location': location.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error toggling favorite status: {str(e)}")
            return {'success': False, 'message': str(e)} 