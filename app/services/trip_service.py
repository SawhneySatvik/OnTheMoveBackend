from datetime import datetime
from app.utils.supabase_client import supabase, supabase_admin
from app.models.trip import Trip
from app.services.vehicle_service import VehicleService
import logging
import math

# Set up logging
logger = logging.getLogger(__name__)

class TripService:
    """Service for handling trip operations."""
    
    @staticmethod
    def get_trips(filters=None):
        """Get all trips with optional filters."""
        try:
            logger.info(f"Getting trips with filters: {filters}")
            
            # Start with a base query
            query = supabase_admin.table('trips').select('*')
            
            # Apply filters if provided
            if filters:
                if 'driver_id' in filters:
                    query = query.eq('driver_id', filters['driver_id'])
                if 'status' in filters:
                    query = query.eq('status', filters['status'])
                if 'start_time_after' in filters:
                    query = query.gte('start_time', filters['start_time_after'])
                if 'start_time_before' in filters:
                    query = query.lte('start_time', filters['start_time_before'])
            
            # Execute the query
            response = query.execute()
            
            trips = [Trip.from_dict(trip).to_dict() for trip in response.data]
            logger.info(f"Found {len(trips)} trips")
            
            return {
                'success': True,
                'trips': trips
            }
            
        except Exception as e:
            logger.error(f"Error getting trips: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_trip_by_id(trip_id):
        """Get a trip by ID."""
        try:
            logger.info(f"Getting trip by ID: {trip_id}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('trips').select('*').eq('id', trip_id).execute()
            
            if not response.data:
                logger.info(f"Trip not found: {trip_id}")
                return {'success': False, 'message': 'Trip not found'}
            
            trip = Trip.from_dict(response.data[0])
            logger.info(f"Found trip: {trip_id}")
            
            # Get vehicle information if vehicle_id exists
            trip_data = trip.to_dict()
            
            if trip.vehicle_id:
                vehicle = VehicleService.get_vehicle_by_id(trip.vehicle_id)
                if vehicle['success']:
                    trip_data['vehicle'] = vehicle['vehicle']
            
            return {
                'success': True,
                'trip': trip_data
            }
            
        except Exception as e:
            logger.error(f"Error getting trip: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def create_trip(driver_id, data):
        """Create a new trip."""
        try:
            logger.info(f"Creating trip for driver: {driver_id}")
            
            # Validate vehicle belongs to driver
            vehicle_response = VehicleService.get_vehicle_by_id(data.get('vehicle_id'), driver_id)
            if not vehicle_response['success']:
                logger.warning(f"Vehicle not found or does not belong to driver: {data.get('vehicle_id')}")
                return {'success': False, 'message': 'Vehicle not found or does not belong to driver'}
            
            # Validate required fields
            required_fields = [
                'start_latitude', 'start_longitude', 'start_address',
                'end_latitude', 'end_longitude', 'end_address',
                'start_time', 'available_seats', 'price'
            ]
            
            for field in required_fields:
                if field not in data or not data.get(field):
                    logger.warning(f"Missing required field: {field}")
                    return {'success': False, 'message': f'Missing required field: {field}'}
            
            # Create trip
            trip_data = {
                'driver_id': driver_id,
                'vehicle_id': data.get('vehicle_id'),
                'start_latitude': data.get('start_latitude'),
                'start_longitude': data.get('start_longitude'),
                'start_address': data.get('start_address'),
                'end_latitude': data.get('end_latitude'),
                'end_longitude': data.get('end_longitude'),
                'end_address': data.get('end_address'),
                'start_time': data.get('start_time'),
                'end_time': data.get('end_time'),
                'status': 'scheduled',
                'available_seats': data.get('available_seats'),
                'price': data.get('price'),
                'description': data.get('description', ''),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('trips').insert(trip_data).execute()
            
            if not response.data:
                logger.error("Failed to create trip")
                return {'success': False, 'message': 'Failed to create trip'}
            
            trip = Trip.from_dict(response.data[0])
            logger.info(f"Trip created successfully: {trip.id}")
            
            return {
                'success': True,
                'trip': trip.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating trip: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_trip(trip_id, driver_id, data):
        """Update a trip."""
        try:
            logger.info(f"Updating trip: {trip_id} for driver: {driver_id}")
            
            # Check if trip exists and belongs to driver
            response = supabase_admin.table('trips').select('*').eq('id', trip_id).eq('driver_id', driver_id).execute()
            
            if not response.data:
                logger.info(f"Trip not found or does not belong to driver: {trip_id}")
                return {'success': False, 'message': 'Trip not found or does not belong to driver'}
            
            # Get current trip
            current_trip = Trip.from_dict(response.data[0])
            
            # Check if trip can be updated based on status
            if current_trip.status not in ['scheduled']:
                logger.warning(f"Cannot update trip with status: {current_trip.status}")
                return {'success': False, 'message': f'Cannot update trip with status: {current_trip.status}'}
            
            # Update trip
            allowed_fields = [
                'vehicle_id', 
                'start_latitude', 'start_longitude', 'start_address',
                'end_latitude', 'end_longitude', 'end_address',
                'start_time', 'end_time', 'available_seats', 'price', 'description'
            ]
            update_data = {k: v for k, v in data.items() if k in allowed_fields}
            
            update_data['updated_at'] = datetime.utcnow().isoformat()
            logger.info(f"Updating trip fields: {', '.join(update_data.keys())}")
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('trips').update(update_data).eq('id', trip_id).eq('driver_id', driver_id).execute()
            
            if not response.data:
                logger.error("Failed to update trip")
                return {'success': False, 'message': 'Failed to update trip'}
            
            trip = Trip.from_dict(response.data[0])
            logger.info(f"Trip updated successfully: {trip_id}")
            
            return {
                'success': True,
                'trip': trip.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error updating trip: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def cancel_trip(trip_id, driver_id):
        """Cancel a trip."""
        try:
            logger.info(f"Cancelling trip: {trip_id} for driver: {driver_id}")
            
            # Check if trip exists and belongs to driver
            response = supabase_admin.table('trips').select('*').eq('id', trip_id).eq('driver_id', driver_id).execute()
            
            if not response.data:
                logger.info(f"Trip not found or does not belong to driver: {trip_id}")
                return {'success': False, 'message': 'Trip not found or does not belong to driver'}
            
            # Get current trip
            current_trip = Trip.from_dict(response.data[0])
            
            # Check if trip can be cancelled based on status
            if current_trip.status not in ['scheduled']:
                logger.warning(f"Cannot cancel trip with status: {current_trip.status}")
                return {'success': False, 'message': f'Cannot cancel trip with status: {current_trip.status}'}
            
            # Update trip status
            update_data = {
                'status': 'cancelled',
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('trips').update(update_data).eq('id', trip_id).eq('driver_id', driver_id).execute()
            
            if not response.data:
                logger.error("Failed to cancel trip")
                return {'success': False, 'message': 'Failed to cancel trip'}
            
            trip = Trip.from_dict(response.data[0])
            logger.info(f"Trip cancelled successfully: {trip_id}")
            
            # TODO: Cancel all associated ride requests
            
            return {
                'success': True,
                'trip': trip.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error cancelling trip: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def start_trip(trip_id, driver_id):
        """Start a trip."""
        try:
            logger.info(f"Starting trip: {trip_id} for driver: {driver_id}")
            
            # Check if trip exists and belongs to driver
            response = supabase_admin.table('trips').select('*').eq('id', trip_id).eq('driver_id', driver_id).execute()
            
            if not response.data:
                logger.info(f"Trip not found or does not belong to driver: {trip_id}")
                return {'success': False, 'message': 'Trip not found or does not belong to driver'}
            
            # Get current trip
            current_trip = Trip.from_dict(response.data[0])
            
            # Check if trip can be started based on status
            if current_trip.status != 'scheduled':
                logger.warning(f"Cannot start trip with status: {current_trip.status}")
                return {'success': False, 'message': f'Cannot start trip with status: {current_trip.status}'}
            
            # Update trip status
            update_data = {
                'status': 'in_progress',
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('trips').update(update_data).eq('id', trip_id).eq('driver_id', driver_id).execute()
            
            if not response.data:
                logger.error("Failed to start trip")
                return {'success': False, 'message': 'Failed to start trip'}
            
            trip = Trip.from_dict(response.data[0])
            logger.info(f"Trip started successfully: {trip_id}")
            
            return {
                'success': True,
                'trip': trip.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error starting trip: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def complete_trip(trip_id, driver_id):
        """Complete a trip."""
        try:
            logger.info(f"Completing trip: {trip_id} for driver: {driver_id}")
            
            # Check if trip exists and belongs to driver
            response = supabase_admin.table('trips').select('*').eq('id', trip_id).eq('driver_id', driver_id).execute()
            
            if not response.data:
                logger.info(f"Trip not found or does not belong to driver: {trip_id}")
                return {'success': False, 'message': 'Trip not found or does not belong to driver'}
            
            # Get current trip
            current_trip = Trip.from_dict(response.data[0])
            
            # Check if trip can be completed based on status
            if current_trip.status != 'in_progress':
                logger.warning(f"Cannot complete trip with status: {current_trip.status}")
                return {'success': False, 'message': f'Cannot complete trip with status: {current_trip.status}'}
            
            # Update trip status
            update_data = {
                'status': 'completed',
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use supabase_admin to bypass RLS policies
            response = supabase_admin.table('trips').update(update_data).eq('id', trip_id).eq('driver_id', driver_id).execute()
            
            if not response.data:
                logger.error("Failed to complete trip")
                return {'success': False, 'message': 'Failed to complete trip'}
            
            trip = Trip.from_dict(response.data[0])
            logger.info(f"Trip completed successfully: {trip_id}")
            
            # TODO: Update all associated ride requests to completed
            
            return {
                'success': True,
                'trip': trip.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error completing trip: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def search_trips(filters):
        """Search for trips based on filters."""
        try:
            logger.info(f"Searching trips with filters: {filters}")
            
            # Start with a base query
            query = supabase_admin.table('trips').select('*')
            
            # Apply filters
            if 'status' in filters:
                query = query.eq('status', filters['status'])
            else:
                # Default to scheduled trips
                query = query.eq('status', 'scheduled')
            
            if 'start_time_after' in filters:
                query = query.gte('start_time', filters['start_time_after'])
            
            if 'start_time_before' in filters:
                query = query.lte('start_time', filters['start_time_before'])
            
            if 'min_available_seats' in filters:
                query = query.gte('available_seats', filters['min_available_seats'])
            
            if 'max_price' in filters:
                query = query.lte('price', filters['max_price'])
            
            # Execute the query
            response = query.execute()
            
            trips = [Trip.from_dict(trip).to_dict() for trip in response.data]
            
            # Apply coordinate-based filtering if provided
            if 'near_latitude' in filters and 'near_longitude' in filters and 'radius_km' in filters:
                lat = float(filters['near_latitude'])
                lng = float(filters['near_longitude'])
                radius = float(filters['radius_km'])
                
                # Filter trips by distance
                filtered_trips = []
                for trip in trips:
                    # Calculate distance to start location
                    distance = TripService.calculate_distance(
                        lat, lng, 
                        float(trip['start_latitude']), float(trip['start_longitude'])
                    )
                    if distance <= radius:
                        trip['distance_km'] = round(distance, 2)
                        filtered_trips.append(trip)
                
                trips = filtered_trips
            
            logger.info(f"Found {len(trips)} trips matching search criteria")
            
            return {
                'success': True,
                'trips': trips
            }
            
        except Exception as e:
            logger.error(f"Error searching trips: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers using the Haversine formula."""
        # Radius of the Earth in kilometers
        R = 6371.0
        
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences in coordinates
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        # Haversine formula
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    @staticmethod
    def get_trip_stats(user_id):
        """Get trip statistics for a user."""
        try:
            logger.info(f"Getting trip statistics for user: {user_id}")
            
            # Get trips as driver
            driver_trips_response = supabase_admin.table('trips').select('*').eq('driver_id', user_id).execute()
            driver_trips = [Trip.from_dict(trip) for trip in driver_trips_response.data]
            
            # Count trips by status
            trips_as_driver = {
                'total': len(driver_trips),
                'scheduled': sum(1 for trip in driver_trips if trip.status == 'scheduled'),
                'in_progress': sum(1 for trip in driver_trips if trip.status == 'in_progress'),
                'completed': sum(1 for trip in driver_trips if trip.status == 'completed'),
                'cancelled': sum(1 for trip in driver_trips if trip.status == 'cancelled')
            }
            
            # Calculate total distance and earnings (for completed trips)
            total_distance_km = 0
            total_earnings = 0
            
            for trip in driver_trips:
                if trip.status == 'completed':
                    # Calculate distance using start and end coordinates
                    distance = TripService.calculate_distance(
                        float(trip.start_latitude), float(trip.start_longitude),
                        float(trip.end_latitude), float(trip.end_longitude)
                    )
                    total_distance_km += distance
                    
                    # Calculate earnings based on price and accepted ride requests
                    ride_requests_response = supabase_admin.table('ride_requests').select('*').eq('trip_id', trip.id).eq('status', 'accepted').execute()
                    passengers_count = sum(int(req['seats_requested']) for req in ride_requests_response.data)
                    total_earnings += float(trip.price) * passengers_count
            
            # Get ride requests as passenger
            passenger_requests_response = supabase_admin.table('ride_requests').select('*').eq('passenger_id', user_id).execute()
            passenger_requests = passenger_requests_response.data
            
            # Count ride requests by status
            rides_as_passenger = {
                'total': len(passenger_requests),
                'pending': sum(1 for req in passenger_requests if req['status'] == 'pending'),
                'accepted': sum(1 for req in passenger_requests if req['status'] == 'accepted'),
                'completed': sum(1 for req in passenger_requests if req['status'] == 'completed'),
                'rejected': sum(1 for req in passenger_requests if req['status'] == 'rejected'),
                'cancelled': sum(1 for req in passenger_requests if req['status'] == 'cancelled')
            }
            
            return {
                'success': True,
                'stats': {
                    'trips_as_driver': trips_as_driver,
                    'rides_as_passenger': rides_as_passenger,
                    'total_distance_km': round(total_distance_km, 2),
                    'total_earnings': round(total_earnings, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting trip statistics: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_trip_history(user_id, filters=None):
        """Get trip history for a user."""
        try:
            logger.info(f"Getting trip history for user: {user_id} with filters: {filters}")
            
            # Initialize empty list for trips
            trips = []
            
            # Determine which trips to include based on role
            role = filters.get('role', 'both') if filters else 'both'
            
            # Get trips as driver
            if role in ['driver', 'both']:
                driver_query = supabase_admin.table('trips').select('*').eq('driver_id', user_id)
                
                # Apply filters
                if filters:
                    if 'status' in filters:
                        driver_query = driver_query.eq('status', filters['status'])
                    if 'from_date' in filters:
                        driver_query = driver_query.gte('start_time', filters['from_date'])
                    if 'to_date' in filters:
                        driver_query = driver_query.lte('start_time', filters['to_date'])
                
                driver_trips_response = driver_query.execute()
                
                for trip_data in driver_trips_response.data:
                    trip = Trip.from_dict(trip_data)
                    
                    # Get passenger count
                    passengers_response = supabase_admin.table('ride_requests').select('*').eq('trip_id', trip.id).eq('status', 'accepted').execute()
                    passenger_count = sum(int(req['seats_requested']) for req in passengers_response.data)
                    
                    # Format trip for history
                    trip_history = {
                        'id': trip.id,
                        'role': 'driver',
                        'start_address': trip.start_address,
                        'end_address': trip.end_address,
                        'start_time': trip.start_time,
                        'status': trip.status,
                        'passengers': passenger_count,
                        'price': float(trip.price),
                        'created_at': trip.created_at
                    }
                    
                    # Add completed_at if available
                    if trip.status == 'completed' and trip.updated_at:
                        trip_history['completed_at'] = trip.updated_at
                    
                    trips.append(trip_history)
            
            # Get trips as passenger
            if role in ['passenger', 'both']:
                passenger_query = supabase_admin.table('ride_requests').select('*, trips(*)').eq('passenger_id', user_id)
                
                # Apply filters
                if filters:
                    if 'status' in filters:
                        passenger_query = passenger_query.eq('status', filters['status'])
                
                passenger_trips_response = passenger_query.execute()
                
                for req_data in passenger_trips_response.data:
                    if not req_data['trips']:
                        continue
                    
                    trip_data = req_data['trips']
                    
                    # Skip if trip doesn't match date filters
                    if filters:
                        if 'from_date' in filters and trip_data['start_time'] < filters['from_date']:
                            continue
                        if 'to_date' in filters and trip_data['start_time'] > filters['to_date']:
                            continue
                    
                    # Format trip for history
                    trip_history = {
                        'id': trip_data['id'],
                        'ride_request_id': req_data['id'],
                        'role': 'passenger',
                        'start_address': req_data['pickup_address'],
                        'end_address': req_data['dropoff_address'],
                        'start_time': trip_data['start_time'],
                        'status': req_data['status'],
                        'seats': req_data['seats_requested'],
                        'price': float(trip_data['price']),
                        'created_at': req_data['created_at']
                    }
                    
                    # Add completed_at if available
                    if req_data['status'] == 'completed' and req_data['updated_at']:
                        trip_history['completed_at'] = req_data['updated_at']
                    
                    trips.append(trip_history)
            
            # Sort trips by start_time (descending)
            trips.sort(key=lambda x: x['start_time'], reverse=True)
            
            # Apply pagination
            page = int(filters.get('page', 1)) if filters else 1
            limit = int(filters.get('limit', 10)) if filters else 10
            
            total_trips = len(trips)
            total_pages = math.ceil(total_trips / limit)
            
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            
            paginated_trips = trips[start_idx:end_idx]
            
            return {
                'success': True,
                'history': {
                    'trips': paginated_trips,
                    'pagination': {
                        'total': total_trips,
                        'page': page,
                        'limit': limit,
                        'pages': total_pages
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting trip history: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_trip_participants(trip_id, user_id=None):
        """Get participants (driver and passengers) for a trip."""
        try:
            logger.info(f"Getting participants for trip: {trip_id}")
            
            # Get trip
            trip_response = TripService.get_trip_by_id(trip_id)
            if not trip_response['success']:
                return trip_response
            
            trip = trip_response['trip']
            
            # Check authorization if user_id is provided
            if user_id:
                # User must be the driver, a passenger, or have a pending request
                is_driver = trip['driver_id'] == user_id
                
                if not is_driver:
                    # Check if user is a passenger or has a pending request
                    ride_request_response = supabase_admin.table('ride_requests').select('*').eq('trip_id', trip_id).eq('passenger_id', user_id).execute()
                    
                    if not ride_request_response.data:
                        logger.warning(f"User {user_id} is not authorized to view participants for trip {trip_id}")
                        return {'success': False, 'message': 'Not authorized to view trip participants'}
            
            # Get driver information
            driver_response = supabase_admin.table('users').select('id, name, profile_image_url, phone').eq('id', trip['driver_id']).execute()
            
            if not driver_response.data:
                logger.warning(f"Driver not found for trip: {trip_id}")
                return {'success': False, 'message': 'Driver not found'}
            
            driver = driver_response.data[0]
            
            # Get passengers (accepted ride requests)
            passengers_response = supabase_admin.table('ride_requests').select('*, users:passenger_id(id, name, profile_image_url)').eq('trip_id', trip_id).in_('status', ['accepted', 'completed']).execute()
            
            passengers = []
            for req in passengers_response.data:
                if not req['users']:
                    continue
                
                passenger = {
                    'id': req['users']['id'],
                    'name': req['users']['name'],
                    'profile_image_url': req['users']['profile_image_url'],
                    'pickup_address': req['pickup_address'],
                    'dropoff_address': req['dropoff_address'],
                    'seats': req['seats_requested'],
                    'status': req['status']
                }
                
                passengers.append(passenger)
            
            return {
                'success': True,
                'participants': {
                    'driver': driver,
                    'passengers': passengers
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting trip participants: {str(e)}")
            return {'success': False, 'message': str(e)} 
        

    @staticmethod
    def get_upcoming_trips(user_id, role='both'):
        """Get upcoming trips for a user with enriched data."""
        try:
            logger.info(f"Fetching upcoming trips for user: {user_id}, role: {role}")
            now = datetime.now().isoformat()
            
            upcoming_trips = []
            
            # Fetch trips as driver
            if role in ['driver', 'both']:
                driver_query = supabase_admin.table('trips').select('*')\
                    .eq('driver_id', user_id)\
                    .eq('status', 'scheduled')\
                    .gt('start_time', now)\
                    .execute()
                
                for trip_data in driver_query.data:
                    trip = Trip.from_dict(trip_data)
                    enriched_trip = TripService.enrich_trip_data(trip, user_id, is_driver=True)
                    upcoming_trips.append(enriched_trip)
            
            # Fetch trips as passenger
            if role in ['passenger', 'both']:
                passenger_query = supabase_admin.table('ride_requests').select('*, trips(*)')\
                    .eq('passenger_id', user_id)\
                    .in_('status', ['accepted', 'pending'])\
                    .execute()
                
                for req_data in passenger_query.data:
                    if not req_data['trips'] or req_data['trips']['status'] != 'scheduled' or req_data['trips']['start_time'] <= now:
                        continue
                    trip = Trip.from_dict(req_data['trips'])
                    enriched_trip = TripService.enrich_trip_data(trip, user_id, is_driver=False)
                    upcoming_trips.append(enriched_trip)
            
            # Sort by start_time
            upcoming_trips.sort(key=lambda x: x['start_time'])
            
            logger.info(f"Found {len(upcoming_trips)} upcoming trips for user: {user_id}")
            return {
                'success': True,
                'trips': upcoming_trips
            }
        
        except Exception as e:
            logger.error(f"Error fetching upcoming trips: {str(e)}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def enrich_trip_data(trip, user_id, is_driver):
        """Enrich trip data with participants and metrics."""
        # Get driver info
        driver_response = supabase_admin.table('users').select('id, name, profile_image_url')\
            .eq('id', trip.driver_id).execute()
        driver = driver_response.data[0] if driver_response.data else {'id': trip.driver_id, 'name': 'Unknown', 'profile_image_url': None}
        
        # Get passengers (accepted only)
        passengers_response = supabase_admin.table('ride_requests').select('seats_requested')\
            .eq('trip_id', trip.id).eq('status', 'accepted').execute()
        passengers_count = sum(int(req['seats_requested']) for req in passengers_response.data)
        
        # Calculate distance and duration
        distance = TripService.calculate_distance(
            float(trip.start_latitude), float(trip.start_longitude),
            float(trip.end_latitude), float(trip.end_longitude)
        )
        duration = int(distance / 40.0 * 60)  # Assuming 40 km/h average speed
        
        return {
            'id': trip.id,
            'source_address': trip.start_address,
            'destination_address': trip.end_address,
            'start_time': trip.start_time,  # ISO 8601 string
            'cost': float(trip.price),
            'seats': trip.available_seats,
            'passengers_count': passengers_count,
            'vehicle_id': trip.vehicle_id,
            'creator_name': driver['name'],
            'creator_image_url': driver['profile_image_url'],
            'distance': round(distance, 1),
            'duration': duration,
            'is_creator': is_driver
        }
    
    @staticmethod
    def search_enriched_trips(user_id, filters):
        """Search for scheduled trips with enriched data."""
        try:
            logger.info(f"Searching enriched trips with filters: {filters}")
            
            query = supabase_admin.table('trips').select('*, users:driver_id(id, name, profile_image_url, institute)')\
                .eq('status', filters['status'])\
                .gt('start_time', filters['start_time_after'])
            
            if filters.get('min_available_seats'):
                query = query.gte('available_seats', int(filters['min_available_seats']))
            if filters.get('max_price'):
                query = query.lte('price', float(filters['max_price']))
            
            response = query.execute()
            trips = response.data
            
            # Filter by location if provided
            if filters.get('near_latitude') and filters.get('near_longitude'):
                lat = float(filters['near_latitude'])
                lng = float(filters['near_longitude'])
                radius = float(filters['radius_km'])
                
                filtered_trips = []
                for trip_data in trips:
                    trip = Trip.from_dict(trip_data)
                    distance = TripService.calculate_distance(
                        lat, lng, float(trip.start_latitude), float(trip.start_longitude)
                    )
                    if distance <= radius and trip.driver_id != user_id:  # Exclude user's own trips
                        enriched_trip = {
                            'id': trip.id,
                            'driver': {
                                'id': trip_data['users']['id'],
                                'name': trip_data['users']['name'],
                                'profile_image_url': trip_data['users']['profile_image_url'],
                                'institute': trip_data['users']['institute']
                            },
                            'departure_time': trip.start_time,
                            'price': str(trip.price),  # String to match RidePreview
                            'available_seats': trip.available_seats,
                            'distance': f"{round(distance, 1)} km"  # String to match RidePreview
                        }
                        filtered_trips.append(enriched_trip)
                trips = filtered_trips
            else:
                trips = [TripService.enrich_search_trip(Trip.from_dict(trip_data), trip_data['users']) 
                        for trip_data in trips if trip_data['driver_id'] != user_id]
            
            logger.info(f"Found {len(trips)} enriched trips")
            return {
                'success': True,
                'trips': trips
            }
        
        except Exception as e:
            logger.error(f"Error searching enriched trips: {str(e)}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def enrich_search_trip(trip, driver_data):
        """Enrich trip data for search results."""
        distance = TripService.calculate_distance(
            float(trip.start_latitude), float(trip.start_longitude),
            float(trip.end_latitude), float(trip.end_longitude)
        )
        return {
            'id': trip.id,
            'driver': {
                'id': driver_data['id'],
                'name': driver_data['name'],
                'profile_image_url': driver_data['profile_image_url'],
                'institute': driver_data.get('institute')
            },
            'departure_time': trip.start_time,
            'price': str(trip.price),
            'available_seats': trip.available_seats,
            'distance': f"{round(distance, 1)} km"
        }