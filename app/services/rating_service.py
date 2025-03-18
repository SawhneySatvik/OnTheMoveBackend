from datetime import datetime
from app.utils.supabase_client import supabase, supabase_admin
from app.models.rating import Rating
from app.services.trip_service import TripService
import logging

# Set up logging
logger = logging.getLogger(__name__)

class RatingService:
    """Service for handling rating operations."""
    
    @staticmethod
    def get_ratings(user_id, as_rater=False):
        """Get all ratings for a user."""
        try:
            logger.info(f"Getting ratings for user: {user_id}, as_rater: {as_rater}")
            
            # Use supabase_admin to bypass RLS policies
            query = supabase_admin.table('ratings').select('*')
            
            if as_rater:
                # Get ratings given by the user
                query = query.eq('rater_id', user_id)
            else:
                # Get ratings received by the user
                query = query.eq('rated_user_id', user_id)
            
            response = query.execute()
            
            ratings = [Rating.from_dict(rating).to_dict() for rating in response.data]
            logger.info(f"Found {len(ratings)} ratings for user: {user_id}")
            
            # Enrich ratings with trip and user information
            for rating in ratings:
                # Get trip information
                trip_response = TripService.get_trip_by_id(rating['trip_id'])
                if trip_response['success']:
                    rating['trip'] = trip_response['trip']
                
                # Get rater information
                rater_response = supabase_admin.table('users').select('id, name, profile_image_url').eq('id', rating['rater_id']).execute()
                if rater_response.data:
                    rating['rater'] = rater_response.data[0]
                
                # Get rated user information
                rated_user_response = supabase_admin.table('users').select('id, name, profile_image_url').eq('id', rating['rated_user_id']).execute()
                if rated_user_response.data:
                    rating['rated_user'] = rated_user_response.data[0]
            
            return {
                'success': True,
                'ratings': ratings
            }
            
        except Exception as e:
            logger.error(f"Error getting ratings: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_rating_by_id(rating_id, user_id=None):
        """Get a rating by ID."""
        try:
            logger.info(f"Getting rating by ID: {rating_id}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('ratings').select('*').eq('id', rating_id).execute()
            
            if not response.data:
                logger.info(f"Rating not found: {rating_id}")
                return {'success': False, 'message': 'Rating not found'}
            
            rating = Rating.from_dict(response.data[0])
            
            # Check if user is authorized to view this rating
            if user_id and user_id != rating.rater_id and user_id != rating.rated_user_id:
                # Check if user is the driver of the trip
                trip_response = TripService.get_trip_by_id(rating.trip_id)
                if not trip_response['success'] or trip_response['trip']['driver_id'] != user_id:
                    logger.warning(f"User {user_id} is not authorized to view rating {rating_id}")
                    return {'success': False, 'message': 'Not authorized to view this rating'}
            
            rating_data = rating.to_dict()
            
            # Enrich rating with trip and user information
            # Get trip information
            trip_response = TripService.get_trip_by_id(rating.trip_id)
            if trip_response['success']:
                rating_data['trip'] = trip_response['trip']
            
            # Get rater information
            rater_response = supabase_admin.table('users').select('id, name, profile_image_url').eq('id', rating.rater_id).execute()
            if rater_response.data:
                rating_data['rater'] = rater_response.data[0]
            
            # Get rated user information
            rated_user_response = supabase_admin.table('users').select('id, name, profile_image_url').eq('id', rating.rated_user_id).execute()
            if rated_user_response.data:
                rating_data['rated_user'] = rated_user_response.data[0]
            
            return {
                'success': True,
                'rating': rating_data
            }
            
        except Exception as e:
            logger.error(f"Error getting rating: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def submit_rating(rater_id, data):
        """Submit a rating for a trip."""
        try:
            logger.info(f"Submitting rating from user: {rater_id}")
            
            trip_id = data.get('trip_id')
            rated_user_id = data.get('rated_user_id')
            
            # Check if trip exists
            trip_response = TripService.get_trip_by_id(trip_id)
            if not trip_response['success']:
                logger.warning(f"Trip not found: {trip_id}")
                return {'success': False, 'message': 'Trip not found'}
            
            trip = trip_response['trip']
            
            # Check if trip is completed
            if trip['status'] != 'completed':
                logger.warning(f"Cannot rate a trip with status: {trip['status']}")
                return {'success': False, 'message': f"Cannot rate a trip with status: {trip['status']}. Trip must be completed."}
            
            # Check if user was part of the trip
            is_driver = trip['driver_id'] == rater_id
            
            if not is_driver:
                # Check if user was a passenger
                ride_request_response = supabase_admin.table('ride_requests').select('*').eq('trip_id', trip_id).eq('passenger_id', rater_id).eq('status', 'accepted').execute()
                
                if not ride_request_response.data:
                    logger.warning(f"User {rater_id} was not part of trip {trip_id}")
                    return {'success': False, 'message': 'You were not part of this trip'}
            
            # Check if rated user was part of the trip
            is_rated_driver = trip['driver_id'] == rated_user_id
            
            if not is_rated_driver:
                # Check if rated user was a passenger
                ride_request_response = supabase_admin.table('ride_requests').select('*').eq('trip_id', trip_id).eq('passenger_id', rated_user_id).eq('status', 'accepted').execute()
                
                if not ride_request_response.data:
                    logger.warning(f"User {rated_user_id} was not part of trip {trip_id}")
                    return {'success': False, 'message': 'The user you are rating was not part of this trip'}
            
            # Check if user has already rated this user for this trip
            existing_rating = supabase_admin.table('ratings').select('*').eq('trip_id', trip_id).eq('rater_id', rater_id).eq('rated_user_id', rated_user_id).execute()
            
            if existing_rating.data:
                logger.warning(f"User {rater_id} has already rated user {rated_user_id} for trip {trip_id}")
                return {'success': False, 'message': 'You have already rated this user for this trip'}
            
            # Create rating
            rating_data = {
                'trip_id': trip_id,
                'rater_id': rater_id,
                'rated_user_id': rated_user_id,
                'rating': data.get('rating'),
                'comment': data.get('comment', ''),
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('ratings').insert(rating_data).execute()
            
            if not response.data:
                logger.error("Failed to submit rating")
                return {'success': False, 'message': 'Failed to submit rating'}
            
            rating = Rating.from_dict(response.data[0])
            logger.info(f"Rating submitted successfully: {rating.id}")
            
            # Update user's average rating
            RatingService.update_user_average_rating(rated_user_id)
            
            return {
                'success': True,
                'message': 'Rating submitted successfully',
                'rating': rating.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error submitting rating: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_user_ratings(user_id):
        """Get all ratings for a specific user."""
        try:
            logger.info(f"Getting ratings for user: {user_id}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('ratings').select('*').eq('rated_user_id', user_id).execute()
            
            ratings = [Rating.from_dict(rating).to_dict() for rating in response.data]
            logger.info(f"Found {len(ratings)} ratings for user: {user_id}")
            
            # Calculate average rating
            if ratings:
                average_rating = sum(rating['rating'] for rating in ratings) / len(ratings)
            else:
                average_rating = 0
            
            # Enrich ratings with trip and rater information
            for rating in ratings:
                # Get trip information
                trip_response = TripService.get_trip_by_id(rating['trip_id'])
                if trip_response['success']:
                    rating['trip'] = trip_response['trip']
                
                # Get rater information
                rater_response = supabase_admin.table('users').select('id, name, profile_image_url').eq('id', rating['rater_id']).execute()
                if rater_response.data:
                    rating['rater'] = rater_response.data[0]
            
            return {
                'success': True,
                'ratings': ratings,
                'average_rating': round(average_rating, 1),
                'total_ratings': len(ratings)
            }
            
        except Exception as e:
            logger.error(f"Error getting user ratings: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_trip_ratings(trip_id, user_id=None):
        """Get all ratings for a specific trip."""
        try:
            logger.info(f"Getting ratings for trip: {trip_id}")
            
            # Check if trip exists
            trip_response = TripService.get_trip_by_id(trip_id)
            if not trip_response['success']:
                logger.warning(f"Trip not found: {trip_id}")
                return {'success': False, 'message': 'Trip not found'}
            
            trip = trip_response['trip']
            
            # Check if user is authorized to view ratings for this trip
            if user_id:
                is_driver = trip['driver_id'] == user_id
                
                if not is_driver:
                    # Check if user was a passenger
                    ride_request_response = supabase_admin.table('ride_requests').select('*').eq('trip_id', trip_id).eq('passenger_id', user_id).execute()
                    
                    if not ride_request_response.data:
                        logger.warning(f"User {user_id} is not authorized to view ratings for trip {trip_id}")
                        return {'success': False, 'message': 'Not authorized to view ratings for this trip'}
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('ratings').select('*').eq('trip_id', trip_id).execute()
            
            ratings = [Rating.from_dict(rating).to_dict() for rating in response.data]
            logger.info(f"Found {len(ratings)} ratings for trip: {trip_id}")
            
            # Enrich ratings with user information
            for rating in ratings:
                # Get rater information
                rater_response = supabase_admin.table('users').select('id, name, profile_image_url').eq('id', rating['rater_id']).execute()
                if rater_response.data:
                    rating['rater'] = rater_response.data[0]
                
                # Get rated user information
                rated_user_response = supabase_admin.table('users').select('id, name, profile_image_url').eq('id', rating['rated_user_id']).execute()
                if rated_user_response.data:
                    rating['rated_user'] = rated_user_response.data[0]
            
            return {
                'success': True,
                'trip': trip,
                'ratings': ratings
            }
            
        except Exception as e:
            logger.error(f"Error getting trip ratings: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_user_average_rating(user_id):
        """Update a user's average rating."""
        try:
            logger.info(f"Updating average rating for user: {user_id}")
            
            # Get all ratings for the user
            response = supabase_admin.table('ratings').select('rating').eq('rated_user_id', user_id).execute()
            
            if not response.data:
                logger.info(f"No ratings found for user: {user_id}")
                return
            
            # Calculate average rating
            ratings = [rating['rating'] for rating in response.data]
            average_rating = sum(ratings) / len(ratings)
            
            # Update user's average rating
            update_data = {
                'average_rating': round(average_rating, 1),
                'total_ratings': len(ratings),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('users').update(update_data).eq('id', user_id).execute()
            
            if not response.data:
                logger.error(f"Failed to update average rating for user: {user_id}")
            else:
                logger.info(f"Average rating updated successfully for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating user average rating: {str(e)}")
            return {'success': False, 'message': str(e)} 