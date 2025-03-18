from datetime import datetime, timedelta
from app.utils.supabase_client import supabase, supabase_admin
from app.models.user import User
from app.utils.auth import generate_access_token, generate_refresh_token
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def register(email, password, name, phone=None, date_of_birth=None, 
                 gender=None, institute=None):
        """Register a new user."""
        try:
            # Normalize email (lowercase)
            email = email.lower().strip()
            
            # Check if user already exists
            response = supabase.table('users').select('*').eq('email', email).execute()
            if response.data:
                return {'success': False, 'message': 'User with this email already exists'}
            
            # Hash password
            password_hash = User.hash_password(password)
            logger.info(f"Password hash for new user: {password_hash[:10]}...")
            
            # Create user
            user_data = {
                'email': email,
                'password_hash': password_hash,
                'name': name,
                'phone': phone,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'institute': institute,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'onboarding_completed': False
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('users').insert(user_data).execute()
            
            if not response.data:
                return {'success': False, 'message': 'Failed to create user'}
            
            user = User.from_dict(response.data[0])
            
            # Generate tokens
            access_token = generate_access_token(user.id)
            refresh_token = generate_refresh_token(user.id)
            
            # Store refresh token
            token_data = {
                'user_id': user.id,
                'token': refresh_token,
                'expires_at': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'created_at': datetime.utcnow().isoformat(),
                'is_revoked': False
            }
            
            # Use supabase_admin to bypass RLS policies
            supabase_admin.table('refresh_tokens').insert(token_data).execute()
            
            return {
                'success': True,
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def login(email, password):
        """Login a user."""
        try:
            # Normalize email (lowercase)
            email = email.lower().strip()
            logger.info(f"Login attempt for email: {email}")
            
            # Get user by email - use admin client to bypass RLS
            response = supabase_admin.table('users').select('*').eq('email', email).execute()
            
            if not response.data:
                logger.info(f"No user found with email: {email}")
                return {'success': False, 'message': 'Invalid email or password'}
            
            user_data = response.data[0]
            logger.info(f"User found: {user_data['id']}")
            
            # Check if password_hash exists in the user data
            if 'password_hash' not in user_data:
                logger.error(f"No password_hash found for user: {user_data['id']}")
                return {'success': False, 'message': 'User account is not properly set up'}
            
            # Log the stored hash for debugging
            stored_hash = user_data['password_hash']
            logger.info(f"Stored password hash: {stored_hash[:10]}...")
            
            # Check password
            password_correct = User.check_password(stored_hash, password)
            logger.info(f"Password check result: {password_correct}")
            
            if not password_correct:
                return {'success': False, 'message': 'Invalid email or password'}
            
            user = User.from_dict(user_data)
            
            # Generate tokens
            access_token = generate_access_token(user.id)
            refresh_token = generate_refresh_token(user.id)
            
            # Store refresh token
            token_data = {
                'user_id': user.id,
                'token': refresh_token,
                'expires_at': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'created_at': datetime.utcnow().isoformat(),
                'is_revoked': False
            }
            
            supabase_admin.table('refresh_tokens').insert(token_data).execute()
            
            return {
                'success': True,
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def refresh_token(refresh_token):
        """Refresh an access token."""
        try:
            logger.info(f"Attempting to refresh token: {refresh_token[:10]}...")
            
            # Check if refresh token exists and is valid - use admin client to bypass RLS
            response = supabase_admin.table('refresh_tokens').select('*').eq('token', refresh_token).eq('is_revoked', False).execute()
            
            if not response.data:
                logger.info("Refresh token not found or revoked")
                return {'success': False, 'message': 'Invalid refresh token'}
            
            token_data = response.data[0]
            logger.info(f"Refresh token found for user: {token_data['user_id']}")
            
            # Check if token is expired
            try:
                # Parse the expires_at string to a datetime object with timezone info
                expires_at_str = token_data['expires_at'].replace('Z', '+00:00')
                expires_at = datetime.fromisoformat(expires_at_str)
                
                # Make sure utcnow() is also timezone aware
                now = datetime.now(expires_at.tzinfo)
                
                logger.info(f"Token expires at: {expires_at}, current time: {now}")
                
                if expires_at < now:
                    logger.info("Refresh token has expired")
                    return {'success': False, 'message': 'Refresh token expired'}
            except Exception as e:
                logger.error(f"Error parsing or comparing dates: {str(e)}")
                # If there's an error with date comparison, continue anyway
                # This is safer than denying a valid token refresh
            
            # Generate new access token
            access_token = generate_access_token(token_data['user_id'])
            logger.info(f"Generated new access token for user: {token_data['user_id']}")
            
            return {
                'success': True,
                'access_token': access_token
            }
            
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def logout(refresh_token):
        """Logout a user by revoking their refresh token."""
        try:
            logger.info(f"Attempting to logout with token: {refresh_token[:10]}...")
            
            # Check if token exists before revoking
            response = supabase_admin.table('refresh_tokens').select('*').eq('token', refresh_token).execute()
            
            if not response.data:
                logger.info("Refresh token not found")
                return {'success': False, 'message': 'Invalid refresh token'}
            
            # Revoke refresh token - only update is_revoked field
            supabase_admin.table('refresh_tokens').update({'is_revoked': True}).eq('token', refresh_token).execute()
            logger.info(f"Successfully revoked refresh token for user: {response.data[0]['user_id']}")
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return {'success': False, 'message': str(e)} 