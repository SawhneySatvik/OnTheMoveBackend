class Person:
    """Person model for interacting with the people table in Supabase."""
    
    def __init__(self, id=None, user_id=None, name=None, email=None, 
                 phone=None, profile_image_url=None, is_favorite=False,
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.profile_image_url = profile_image_url
        self.is_favorite = is_favorite
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_dict(cls, data):
        """Create a Person instance from a dictionary."""
        if not data:
            return None
        
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            profile_image_url=data.get('profile_image_url'),
            is_favorite=data.get('is_favorite', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """Convert Person instance to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'profile_image_url': self.profile_image_url,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 