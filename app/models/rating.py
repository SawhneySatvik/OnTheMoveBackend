class Rating:
    """Model for a rating."""
    
    def __init__(self, id=None, trip_id=None, rater_id=None, rated_user_id=None, 
                 rating=None, comment=None, created_at=None):
        """Initialize a Rating object."""
        self.id = id
        self.trip_id = trip_id
        self.rater_id = rater_id
        self.rated_user_id = rated_user_id
        self.rating = rating
        self.comment = comment
        self.created_at = created_at
    
    @classmethod
    def from_dict(cls, data):
        """Create a Rating object from a dictionary."""
        return cls(
            id=data.get('id'),
            trip_id=data.get('trip_id'),
            rater_id=data.get('rater_id'),
            rated_user_id=data.get('rated_user_id'),
            rating=data.get('rating'),
            comment=data.get('comment'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """Convert a Rating object to a dictionary."""
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'rater_id': self.rater_id,
            'rated_user_id': self.rated_user_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at
        } 