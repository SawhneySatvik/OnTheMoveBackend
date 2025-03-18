class Vehicle:
    """Vehicle model for interacting with the vehicles table in Supabase."""
    
    def __init__(self, id=None, user_id=None, make=None, model=None, year=None,
                 color=None, license_plate=None, capacity=None, image_url=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.make = make
        self.model = model
        self.year = year
        self.color = color
        self.license_plate = license_plate
        self.capacity = capacity
        self.image_url = image_url
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_dict(cls, data):
        """Create a Vehicle instance from a dictionary."""
        if not data:
            return None
        
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            make=data.get('make'),
            model=data.get('model'),
            year=data.get('year'),
            color=data.get('color'),
            license_plate=data.get('license_plate'),
            capacity=data.get('capacity'),
            image_url=data.get('image_url'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """Convert Vehicle instance to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'color': self.color,
            'license_plate': self.license_plate,
            'capacity': self.capacity,
            'image_url': self.image_url,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 