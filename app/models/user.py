from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logger = logging.getLogger(__name__)

class User:
    """User model for interacting with the users table in Supabase."""
    
    def __init__(self, id=None, email=None, name=None, profile_image_url=None, 
                 phone=None, date_of_birth=None, gender=None, institute=None,
                 created_at=None, updated_at=None, onboarding_completed=False,
                 average_rating=None):
        self.id = id
        self.email = email
        self.name = name
        self.profile_image_url = profile_image_url
        self.phone = phone
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.institute = institute
        self.created_at = created_at
        self.updated_at = updated_at
        self.onboarding_completed = onboarding_completed
        self.average_rating = average_rating
    
    @classmethod
    def from_dict(cls, data):
        """Create a User instance from a dictionary."""
        if not data:
            return None
        
        return cls(
            id=data.get('id'),
            email=data.get('email'),
            name=data.get('name'),
            profile_image_url=data.get('profile_image_url'),
            phone=data.get('phone'),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            institute=data.get('institute'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            onboarding_completed=data.get('onboarding_completed', False),
            average_rating=data.get('average_rating')
        )
    
    def to_dict(self):
        """Convert User instance to a dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'profile_image_url': self.profile_image_url,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender,
            'institute': self.institute,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'onboarding_completed': self.onboarding_completed,
            'average_rating': self.average_rating
        }
    
    @staticmethod
    def hash_password(password):
        """Hash a password."""
        hashed = generate_password_hash(password)
        logger.info(f"Generated password hash: {hashed[:10]}...")
        return hashed
    
    @staticmethod
    def check_password(hashed_password, password):
        """Check if a password matches the hash."""
        # Log parameters for debugging
        logger.info(f"Checking password: hash prefix={hashed_password[:10]}...")
        result = check_password_hash(hashed_password, password)
        logger.info(f"Password check result: {result}")
        return result 