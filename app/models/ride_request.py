class RideRequest:
    """RideRequest model for interacting with the ride_requests table in Supabase."""
    
    def __init__(self, id=None, trip_id=None, passenger_id=None, 
                 pickup_latitude=None, pickup_longitude=None, pickup_address=None,
                 dropoff_latitude=None, dropoff_longitude=None, dropoff_address=None,
                 status=None, seats_requested=None, message=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.trip_id = trip_id
        self.passenger_id = passenger_id
        self.pickup_latitude = pickup_latitude
        self.pickup_longitude = pickup_longitude
        self.pickup_address = pickup_address
        self.dropoff_latitude = dropoff_latitude
        self.dropoff_longitude = dropoff_longitude
        self.dropoff_address = dropoff_address
        self.status = status  # 'pending', 'accepted', 'rejected', 'cancelled', 'completed'
        self.seats_requested = seats_requested
        self.message = message
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_dict(cls, data):
        """Create a RideRequest instance from a dictionary."""
        if not data:
            return None
        
        return cls(
            id=data.get('id'),
            trip_id=data.get('trip_id'),
            passenger_id=data.get('passenger_id'),
            pickup_latitude=data.get('pickup_latitude'),
            pickup_longitude=data.get('pickup_longitude'),
            pickup_address=data.get('pickup_address'),
            dropoff_latitude=data.get('dropoff_latitude'),
            dropoff_longitude=data.get('dropoff_longitude'),
            dropoff_address=data.get('dropoff_address'),
            status=data.get('status'),
            seats_requested=data.get('seats_requested'),
            message=data.get('message'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """Convert RideRequest instance to a dictionary."""
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'passenger_id': self.passenger_id,
            'pickup_latitude': self.pickup_latitude,
            'pickup_longitude': self.pickup_longitude,
            'pickup_address': self.pickup_address,
            'dropoff_latitude': self.dropoff_latitude,
            'dropoff_longitude': self.dropoff_longitude,
            'dropoff_address': self.dropoff_address,
            'status': self.status,
            'seats_requested': self.seats_requested,
            'message': self.message,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 