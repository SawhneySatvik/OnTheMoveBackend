class Location:
    """Location model for interacting with the locations table in Supabase."""
    
    def __init__(self, id=None, user_id=None, name=None, address=None, 
                 latitude=None, longitude=None, is_favorite=False,
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.is_favorite = is_favorite
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_dict(cls, data):
        """Create a Location instance from a dictionary."""
        if not data:
            return None
        
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            name=data.get('name'),
            address=data.get('address'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            is_favorite=data.get('is_favorite', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """Convert Location instance to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 