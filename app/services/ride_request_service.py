from datetime import datetime
from app.utils.supabase_client import supabase, supabase_admin
from app.models.ride_request import RideRequest
from app.services.trip_service import TripService
import logging

# Set up logging
logger = logging.getLogger(__name__)

class RideRequestService:
    """Service for handling ride request operations."""
    
    @staticmethod
    def get_ride_requests(user_id, is_driver=False):
        """Get all ride requests for a user."""
        try:
            logger.info(f"Getting ride requests for user: {user_id}, is_driver: {is_driver}")
            
            # Use supabase_admin to bypass RLS policies
            query = supabase_admin.table('ride_requests').select('*')
            
            if is_driver:
                # Get trips where user is the driver
                trips_response = supabase_admin.table('trips').select('id').eq('driver_id', user_id).execute()
                
                if not trips_response.data:
                    logger.info(f"No trips found for driver: {user_id}")
                    return {'success': True, 'ride_requests': []}
                
                trip_ids = [trip['id'] for trip in trips_response.data]
                query = query.in_('trip_id', trip_ids)
            else:
                # Get ride requests where user is the passenger
                query = query.eq('passenger_id', user_id)
            
            response = query.execute()
            
            ride_requests = [RideRequest.from_dict(request).to_dict() for request in response.data]
            logger.info(f"Found {len(ride_requests)} ride requests for user: {user_id}")
            
            # Enrich ride requests with trip information
            for request in ride_requests:
                trip_response = TripService.get_trip_by_id(request['trip_id'])
                if trip_response['success']:
                    request['trip'] = trip_response['trip']
            
            return {
                'success': True,
                'ride_requests': ride_requests
            }
            
        except Exception as e:
            logger.error(f"Error getting ride requests: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_ride_request_by_id(request_id, user_id=None):
        """Get a ride request by ID."""
        try:
            logger.info(f"Getting ride request by ID: {request_id}, user_id: {user_id}")
            
            # Use supabase_admin to bypass RLS policies
            query = supabase_admin.table('ride_requests').select('*').eq('id', request_id)
            
            if user_id:
                # Check if user is the passenger or the driver of the trip
                query = query.eq('passenger_id', user_id)
            
            response = query.execute()
            
            if not response.data:
                logger.info(f"Ride request not found: {request_id}")
                return {'success': False, 'message': 'Ride request not found'}
            
            ride_request = RideRequest.from_dict(response.data[0])
            logger.info(f"Found ride request: {request_id}")
            
            # Get trip information
            trip_response = TripService.get_trip_by_id(ride_request.trip_id)
            
            ride_request_data = ride_request.to_dict()
            if trip_response['success']:
                ride_request_data['trip'] = trip_response['trip']
                
                # If user_id is provided but not the passenger, check if they're the driver
                if user_id and ride_request.passenger_id != user_id:
                    if trip_response['trip']['driver_id'] != user_id:
                        logger.warning(f"User {user_id} is not authorized to view this ride request")
                        return {'success': False, 'message': 'Not authorized to view this ride request'}
            
            return {
                'success': True,
                'ride_request': ride_request_data
            }
            
        except Exception as e:
            logger.error(f"Error getting ride request: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def create_ride_request(passenger_id, data):
        """Create a new ride request."""
        try:
            logger.info(f"Creating ride request for passenger: {passenger_id}")
            
            # Check if trip exists and is scheduled
            trip_response = TripService.get_trip_by_id(data.get('trip_id'))
            if not trip_response['success']:
                logger.warning(f"Trip not found: {data.get('trip_id')}")
                return {'success': False, 'message': 'Trip not found'}
            
            trip = trip_response['trip']
            if trip['status'] != 'scheduled':
                logger.warning(f"Cannot request a ride for a trip with status: {trip['status']}")
                return {'success': False, 'message': f'Cannot request a ride for a trip with status: {trip["status"]}'}
            
            # Check if passenger has already requested this trip
            existing_request = supabase_admin.table('ride_requests').select('*').eq('trip_id', data.get('trip_id')).eq('passenger_id', passenger_id).execute()
            if existing_request.data:
                logger.warning(f"Passenger {passenger_id} has already requested this trip")
                return {'success': False, 'message': 'You have already requested this trip'}
            
            # Check if there are enough available seats
            if trip['available_seats'] < data.get('seats_requested', 1):
                logger.warning(f"Not enough available seats. Requested: {data.get('seats_requested', 1)}, Available: {trip['available_seats']}")
                return {'success': False, 'message': 'Not enough available seats available'}
            
            # Validate required fields
            required_fields = [
                'pickup_latitude', 'pickup_longitude', 'pickup_address',
                'dropoff_latitude', 'dropoff_longitude', 'dropoff_address',
                'seats_requested'
            ]
            
            for field in required_fields:
                if field not in data or not data.get(field):
                    logger.warning(f"Missing required field: {field}")
                    return {'success': False, 'message': f'Missing required field: {field}'}
            
            # Create ride request
            ride_request_data = {
                'trip_id': data.get('trip_id'),
                'passenger_id': passenger_id,
                'pickup_latitude': data.get('pickup_latitude'),
                'pickup_longitude': data.get('pickup_longitude'),
                'pickup_address': data.get('pickup_address'),
                'dropoff_latitude': data.get('dropoff_latitude'),
                'dropoff_longitude': data.get('dropoff_longitude'),
                'dropoff_address': data.get('dropoff_address'),
                'status': 'pending',
                'seats_requested': data.get('seats_requested', 1),
                'message': data.get('message', ''),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('ride_requests').insert(ride_request_data).execute()
            
            if not response.data:
                logger.error("Failed to create ride request")
                return {'success': False, 'message': 'Failed to create ride request'}
            
            ride_request = RideRequest.from_dict(response.data[0])
            logger.info(f"Ride request created successfully: {ride_request.id}")
            
            return {
                'success': True,
                'ride_request': ride_request.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating ride request: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_ride_request_status(request_id, user_id, new_status, is_driver=False):
        """Update the status of a ride request."""
        try:
            logger.info(f"Updating ride request status: {request_id}, user_id: {user_id}, new_status: {new_status}, is_driver: {is_driver}")
            
            # Get the ride request
            response = supabase_admin.table('ride_requests').select('*').eq('id', request_id).execute()
            
            if not response.data:
                logger.info(f"Ride request not found: {request_id}")
                return {'success': False, 'message': 'Ride request not found'}
            
            ride_request = RideRequest.from_dict(response.data[0])
            
            # Check authorization
            if is_driver:
                # Check if user is the driver of the trip
                trip_response = TripService.get_trip_by_id(ride_request.trip_id)
                if not trip_response['success']:
                    logger.warning(f"Trip not found: {ride_request.trip_id}")
                    return {'success': False, 'message': 'Trip not found'}
                
                if trip_response['trip']['driver_id'] != user_id:
                    logger.warning(f"User {user_id} is not the driver of this trip")
                    return {'success': False, 'message': 'Not authorized to update this ride request'}
                
                # Driver can only accept or reject pending requests
                if ride_request.status != 'pending':
                    logger.warning(f"Cannot update ride request with status: {ride_request.status}")
                    return {'success': False, 'message': f'Cannot update ride request with status: {ride_request.status}'}
                
                if new_status not in ['accepted', 'rejected']:
                    logger.warning(f"Invalid status transition from {ride_request.status} to {new_status}")
                    return {'success': False, 'message': f'Invalid status transition from {ride_request.status} to {new_status}'}
                
                # If accepting, check if there are enough seats available
                if new_status == 'accepted':
                    trip = trip_response['trip']
                    
                    # Get all accepted ride requests for this trip
                    accepted_requests = supabase_admin.table('ride_requests').select('*').eq('trip_id', ride_request.trip_id).eq('status', 'accepted').execute()
                    
                    # Calculate total seats taken
                    seats_taken = sum(RideRequest.from_dict(req).seats_requested for req in accepted_requests.data)
                    
                    # Check if there are enough seats available
                    if seats_taken + ride_request.seats_requested > trip['available_seats']:
                        logger.warning(f"Not enough available seats. Requested: {ride_request.seats_requested}, Available: {trip['available_seats'] - seats_taken}")
                        return {'success': False, 'message': 'Not enough available seats'}
            else:
                # Passenger can only cancel their own requests
                if ride_request.passenger_id != user_id:
                    logger.warning(f"User {user_id} is not the passenger of this ride request")
                    return {'success': False, 'message': 'Not authorized to update this ride request'}
                
                if ride_request.status not in ['pending', 'accepted']:
                    logger.warning(f"Cannot cancel ride request with status: {ride_request.status}")
                    return {'success': False, 'message': f'Cannot cancel ride request with status: {ride_request.status}'}
                
                if new_status != 'cancelled':
                    logger.warning(f"Passengers can only cancel ride requests, not {new_status} them")
                    return {'success': False, 'message': f'Passengers can only cancel ride requests, not {new_status} them'}
            
            # Update ride request status
            update_data = {
                'status': new_status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('ride_requests').update(update_data).eq('id', request_id).execute()
            
            if not response.data:
                logger.error("Failed to update ride request status")
                return {'success': False, 'message': 'Failed to update ride request status'}
            
            updated_ride_request = RideRequest.from_dict(response.data[0])
            logger.info(f"Ride request status updated successfully: {updated_ride_request.id}, new status: {updated_ride_request.status}")
            
            return {
                'success': True,
                'message': f'Ride request {new_status} successfully',
                'ride_request': {
                    'id': updated_ride_request.id,
                    'status': updated_ride_request.status,
                    'updated_at': updated_ride_request.updated_at
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating ride request status: {str(e)}")
            return {'success': False, 'message': str(e)} 
        
    @staticmethod
    def get_pending_requests_for_trip(trip_id, user_id):
        """Get pending ride requests for a trip, ensuring the user is the driver."""
        try:
            logger.info(f"Fetching pending requests for trip: {trip_id}, user: {user_id}")
            
            # Verify user is the driver
            trip_response = TripService.get_trip_by_id(trip_id)
            if not trip_response['success'] or trip_response['trip']['driver_id'] != user_id:
                logger.warning(f"User {user_id} not authorized to view requests for trip {trip_id}")
                return {'success': False, 'message': 'Not authorized'}
            
            response = supabase_admin.table('ride_requests').select('*')\
                .eq('trip_id', trip_id)\
                .eq('status', 'pending')\
                .execute()
            
            requests = [RideRequest.from_dict(req).to_dict() for req in response.data]
            logger.info(f"Found {len(requests)} pending requests for trip: {trip_id}")
            return {
                'success': True,
                'ride_requests': requests
            }
        
        except Exception as e:
            logger.error(f"Error fetching pending requests: {str(e)}")
            return {'success': False, 'message': str(e)}
        
    @staticmethod
    def get_pending_requests_for_trip(trip_id, user_id):
        try:
            trip_response = TripService.get_trip_by_id(trip_id)
            if not trip_response['success'] or trip_response['trip']['driver_id'] != user_id:
                return {'success': False, 'message': 'Not authorized'}
            
            response = supabase_admin.table('ride_requests').select('*, users:passenger_id(id, name, profile_image_url, phone)')\
                .eq('trip_id', trip_id)\
                .eq('status', 'pending')\
                .execute()
            
            requests = [RideRequest.from_dict(req).to_dict() for req in response.data]
            for req, raw_data in zip(requests, response.data):
                req['passenger'] = {
                    'id': raw_data['users']['id'],
                    'name': raw_data['users']['name'],
                    'profile_image_url': raw_data['users']['profile_image_url'],
                    'phone': raw_data['users']['phone']
                }
            
            return {'success': True, 'ride_requests': requests}
        except Exception as e:
            return {'success': False, 'message': str(e)}