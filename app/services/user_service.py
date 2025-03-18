from datetime import datetime
from app.utils.supabase_client import supabase, supabase_admin
from app.models.user import User
import logging

# Set up logging
logger = logging.getLogger(__name__)

class UserService:
    """Service for handling user operations."""
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get a user by ID."""
        try:
            logger.info(f"Getting user by ID: {user_id}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('users').select('*').eq('id', user_id).execute()
            
            if not response.data:
                logger.info(f"User not found with ID: {user_id}")
                return {'success': False, 'message': 'User not found'}
            
            user = User.from_dict(response.data[0])
            logger.info(f"User found: {user.name} ({user.email})")
            
            return {
                'success': True,
                'user': user.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_user(user_id, data):
        """Update a user."""
        try:
            logger.info(f"Updating user with ID: {user_id}")
            
            # Check if user exists
            response = supabase_admin.table('users').select('*').eq('id', user_id).execute()
            
            if not response.data:
                logger.info(f"User not found with ID: {user_id}")
                return {'success': False, 'message': 'User not found'}
            
            # Update user
            update_data = {k: v for k, v in data.items() if k in [
                'name', 'phone', 'profile_image_url', 'date_of_birth', 
                'gender', 'institute', 'onboarding_completed'
            ]}
            
            update_data['updated_at'] = datetime.utcnow().isoformat()
            logger.info(f"Updating user fields: {', '.join(update_data.keys())}")
            
            response = supabase_admin.table('users').update(update_data).eq('id', user_id).execute()
            
            if not response.data:
                logger.error("Failed to update user")
                return {'success': False, 'message': 'Failed to update user'}
            
            user = User.from_dict(response.data[0])
            logger.info(f"User updated successfully: {user.name}")
            
            return {
                'success': True,
                'user': user.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def complete_onboarding(user_id):
        """Mark onboarding as completed for a user."""
        try:
            logger.info(f"Completing onboarding for user with ID: {user_id}")
            
            # Update user
            update_data = {
                'onboarding_completed': True,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            response = supabase_admin.table('users').update(update_data).eq('id', user_id).execute()
            
            if not response.data:
                logger.error("Failed to update user onboarding status")
                return {'success': False, 'message': 'Failed to update user'}
            
            logger.info("Onboarding completed successfully")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error completing onboarding: {str(e)}")
            return {'success': False, 'message': str(e)} 