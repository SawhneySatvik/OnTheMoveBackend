class Trip:
    """Trip model for interacting with the trips table in Supabase."""
    
    def __init__(self, id=None, driver_id=None, vehicle_id=None, 
                 start_latitude=None, start_longitude=None, start_address=None,
                 end_latitude=None, end_longitude=None, end_address=None,
                 start_time=None, end_time=None, status=None,
                 available_seats=None, price=None, description=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.driver_id = driver_id
        self.vehicle_id = vehicle_id
        self.start_latitude = start_latitude
        self.start_longitude = start_longitude
        self.start_address = start_address
        self.end_latitude = end_latitude
        self.end_longitude = end_longitude
        self.end_address = end_address
        self.start_time = start_time
        self.end_time = end_time
        self.status = status  # 'scheduled', 'in_progress', 'completed', 'cancelled'
        self.available_seats = available_seats
        self.price = price
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_dict(cls, data):
        """Create a Trip instance from a dictionary."""
        if not data:
            return None
        
        return cls(
            id=data.get('id'),
            driver_id=data.get('driver_id'),
            vehicle_id=data.get('vehicle_id'),
            start_latitude=data.get('start_latitude'),
            start_longitude=data.get('start_longitude'),
            start_address=data.get('start_address'),
            end_latitude=data.get('end_latitude'),
            end_longitude=data.get('end_longitude'),
            end_address=data.get('end_address'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            status=data.get('status'),
            available_seats=data.get('available_seats'),
            price=data.get('price'),
            description=data.get('description'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """Convert Trip instance to a dictionary."""
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'vehicle_id': self.vehicle_id,
            'start_latitude': self.start_latitude,
            'start_longitude': self.start_longitude,
            'start_address': self.start_address,
            'end_latitude': self.end_latitude,
            'end_longitude': self.end_longitude,
            'end_address': self.end_address,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'status': self.status,
            'available_seats': self.available_seats,
            'price': self.price,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 