from datetime import datetime
from app.utils.supabase_client import supabase, supabase_admin
from app.models.person import Person
import logging

# Set up logging
logger = logging.getLogger(__name__)

class PersonService:
    """Service for handling person operations."""
    
    @staticmethod
    def get_user_people(user_id):
        """Get all people for a user."""
        try:
            logger.info(f"Getting people for user: {user_id}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('people').select('*').eq('user_id', user_id).execute()
            
            people = [Person.from_dict(person).to_dict() for person in response.data]
            logger.info(f"Found {len(people)} people for user: {user_id}")
            
            return {
                'success': True,
                'people': people
            }
            
        except Exception as e:
            logger.error(f"Error getting people: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_person_by_id(person_id, user_id=None):
        """Get a person by ID."""
        try:
            logger.info(f"Getting person by ID: {person_id}, user_id: {user_id}")
            
            # Use supabase_admin to bypass RLS policies
            query = supabase_admin.table('people').select('*').eq('id', person_id)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.execute()
            
            if not response.data:
                logger.info(f"Person not found: {person_id}")
                return {'success': False, 'message': 'Person not found'}
            
            person = Person.from_dict(response.data[0])
            logger.info(f"Found person: {person_id}")
            
            return {
                'success': True,
                'person': person.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting person: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def add_person(user_id, data):
        """Add a new person."""
        try:
            logger.info(f"Adding person for user: {user_id}")
            
            # Create person
            person_data = {
                'user_id': user_id,
                'name': data.get('name'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'profile_image_url': data.get('profile_image_url'),
                'is_favorite': data.get('is_favorite', False),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('people').insert(person_data).execute()
            
            if not response.data:
                logger.error("Failed to add person")
                return {'success': False, 'message': 'Failed to add person'}
            
            person = Person.from_dict(response.data[0])
            logger.info(f"Person added successfully: {person.id}")
            
            return {
                'success': True,
                'person': person.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error adding person: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_person(person_id, user_id, data):
        """Update a person."""
        try:
            logger.info(f"Updating person: {person_id} for user: {user_id}")
            
            # Check if person exists and belongs to user
            response = supabase_admin.table('people').select('*').eq('id', person_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.info(f"Person not found or does not belong to user: {person_id}")
                return {'success': False, 'message': 'Person not found or does not belong to user'}
            
            # Update person
            update_data = {k: v for k, v in data.items() if k in [
                'name', 'email', 'phone', 'profile_image_url', 'is_favorite'
            ]}
            
            update_data['updated_at'] = datetime.utcnow().isoformat()
            logger.info(f"Updating person fields: {', '.join(update_data.keys())}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('people').update(update_data).eq('id', person_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.error("Failed to update person")
                return {'success': False, 'message': 'Failed to update person'}
            
            person = Person.from_dict(response.data[0])
            logger.info(f"Person updated successfully: {person_id}")
            
            return {
                'success': True,
                'person': person.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error updating person: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def delete_person(person_id, user_id):
        """Delete a person."""
        try:
            logger.info(f"Deleting person: {person_id} for user: {user_id}")
            
            # Check if person exists and belongs to user
            response = supabase_admin.table('people').select('*').eq('id', person_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.info(f"Person not found or does not belong to user: {person_id}")
                return {'success': False, 'message': 'Person not found or does not belong to user'}
            
            # Delete person
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('people').delete().eq('id', person_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.error("Failed to delete person")
                return {'success': False, 'message': 'Failed to delete person'}
            
            logger.info(f"Person deleted successfully: {person_id}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error deleting person: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def toggle_favorite(person_id, user_id):
        """Toggle the favorite status of a person."""
        try:
            logger.info(f"Toggling favorite status for person: {person_id}, user: {user_id}")
            
            # Check if person exists and belongs to user
            response = supabase_admin.table('people').select('*').eq('id', person_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.info(f"Person not found or does not belong to user: {person_id}")
                return {'success': False, 'message': 'Person not found or does not belong to user'}
            
            # Get current favorite status
            current_person = Person.from_dict(response.data[0])
            new_favorite_status = not current_person.is_favorite
            
            # Update favorite status
            update_data = {
                'is_favorite': new_favorite_status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('people').update(update_data).eq('id', person_id).eq('user_id', user_id).execute()
            
            if not response.data:
                logger.error("Failed to update favorite status")
                return {'success': False, 'message': 'Failed to update favorite status'}
            
            person = Person.from_dict(response.data[0])
            logger.info(f"Favorite status toggled to {person.is_favorite} for person: {person_id}")
            
            return {
                'success': True,
                'person': person.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error toggling favorite status: {str(e)}")
            return {'success': False, 'message': str(e)} 