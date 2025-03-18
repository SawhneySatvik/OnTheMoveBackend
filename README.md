# OnTheMove Backend

This is the backend API for the OnTheMove ride-sharing application. It is built with Flask and uses Supabase as the database.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the root directory with the following variables:
   ```
   # Flask configuration
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   JWT_SECRET_KEY=your_jwt_secret_key_here

   # Supabase configuration
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_anon_key_here
   SUPABASE_SERVICE_KEY=your_supabase_service_key_here

   # JWT configuration
   JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour
   JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 days
   ```
6. Run the application:
   ```
   python run.py
   ```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout and invalidate tokens
- `GET /api/auth/me` - Get current user profile

### Users

- `PUT /api/users/me` - Update current user profile
- `PUT /api/users/complete-onboarding` - Mark onboarding as completed

### Vehicles

- `GET /api/vehicles` - Get all vehicles for current user
- `GET /api/vehicles/<vehicle_id>` - Get vehicle details
- `POST /api/vehicles/add` - Add a new vehicle
- `PUT /api/vehicles/<vehicle_id>/update` - Update vehicle
- `DELETE /api/vehicles/<vehicle_id>/delete` - Delete vehicle

### Locations

- `GET /api/locations` - Get all locations for current user
- `GET /api/locations/<location_id>` - Get location details
- `POST /api/locations/add` - Add a new location
- `PUT /api/locations/<location_id>/update` - Update location
- `DELETE /api/locations/<location_id>/delete` - Delete location
- `PUT /api/locations/<location_id>/favorite` - Toggle favorite status

### People (Contacts)

- `GET /api/people` - Get all contacts for current user
- `GET /api/people/<person_id>` - Get contact details
- `POST /api/people/add` - Add a new contact
- `PUT /api/people/<person_id>/update` - Update contact
- `DELETE /api/people/<person_id>/delete` - Delete contact
- `PUT /api/people/<person_id>/favorite` - Toggle favorite status

### Trips

- `GET /api/trips` - Get all trips with optional filters
- `GET /api/trips/<trip_id>` - Get trip details
- `POST /api/trips/create` - Create a new trip (requires coordinates)
- `PUT /api/trips/<trip_id>/update` - Update trip
- `PUT /api/trips/<trip_id>/cancel` - Cancel trip
- `PUT /api/trips/<trip_id>/start` - Start trip
- `PUT /api/trips/<trip_id>/complete` - Complete trip
- `GET /api/trips/search` - Search for trips based on filters (including location-based search within a radius)

### Ride Requests

- `GET /api/ride-requests` - Get all ride requests for current user
- `GET /api/ride-requests/<request_id>` - Get ride request details
- `POST /api/ride-requests/create` - Create a new ride request (requires coordinates)
- `PUT /api/ride-requests/<request_id>/accept` - Accept ride request (driver only)
- `PUT /api/ride-requests/<request_id>/reject` - Reject ride request (driver only)
- `PUT /api/ride-requests/<request_id>/cancel` - Cancel ride request (passenger only)

### Ratings

- `GET /api/ratings` - Get all ratings for current user (as rated user by default, use `?as_rater=true` to get ratings given by the user)
- `GET /api/ratings/<rating_id>` - Get rating details
- `POST /api/ratings/submit` - Submit a new rating (requires trip_id, rated_user_id, and rating)
- `GET /api/ratings/user/<user_id>` - Get all ratings for a specific user
- `GET /api/ratings/trip/<trip_id>` - Get all ratings for a specific trip

## Location Handling

The OnTheMove backend supports two approaches for handling locations:

### 1. Saved Locations

Users can save locations to their profile for reuse:
- Create a location using `POST /api/locations/add`
- These saved locations can be used for reference but are not directly linked to trips or ride requests

### 2. Direct Coordinates

All trips and ride requests now require direct coordinates:

#### For Trips:
When creating a trip with `POST /api/trips/create`, you must provide:
```json
{
  "vehicle_id": "your_vehicle_id",
  "start_latitude": 37.7749,
  "start_longitude": -122.4194,
  "start_address": "San Francisco, CA",
  "end_latitude": 37.3352,
  "end_longitude": -121.8811,
  "end_address": "San Jose, CA",
  "start_time": "2023-03-20T10:00:00Z",
  "available_seats": 3,
  "price": 15.50
}
```

#### For Ride Requests:
When creating a ride request with `POST /api/ride-requests/create`, you must provide:
```json
{
  "trip_id": "your_trip_id",
  "pickup_latitude": 37.7749,
  "pickup_longitude": -122.4194,
  "pickup_address": "San Francisco, CA",
  "dropoff_latitude": 37.3352,
  "dropoff_longitude": -121.8811,
  "dropoff_address": "San Jose, CA",
  "seats_requested": 2
}
```

#### Location-Based Search:
You can search for trips near a specific location using:
- `GET /api/trips/search?near_latitude=37.7749&near_longitude=-122.4194&radius_km=5`
- This will return trips with starting points within 5 kilometers of the specified coordinates
- Results include a `distance_km` field showing the distance from the search point

## Database Schema

The database schema is defined in Supabase and includes the following tables:

- `users` - User information
- `vehicles` - Vehicle information
- `locations` - Location information
- `people` - Contact information
- `trips` - Trip information with direct coordinates
- `ride_requests` - Ride request information with direct coordinates
- `ratings` - Rating information
- `notifications` - Notification information
- `refresh_tokens` - Refresh token information

## Development

### Project Structure

```
OnTheMoveBackend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── vehicle.py
│   │   └── ...
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── vehicles.py
│   │   └── ...
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── vehicle_service.py
│   │   └── ...
│   └── utils/
│       ├── __init__.py
│       ├── auth.py
│       ├── supabase_client.py
│       └── ...
├── tests/
├── .env
├── .gitignore
├── requirements.txt
└── run.py
```

### Adding New Features

To add a new feature:

1. Create a model in `app/models/`
2. Create a service in `app/services/`
3. Create routes in `app/routes/`
4. Register the blueprint in `app/__init__.py`

### Running Tests

```
pytest
```

## Deployment

The application can be deployed to any platform that supports Python applications, such as Heroku, AWS, or Google Cloud Platform.

### Deploying to Heroku

1. Create a Heroku account
2. Install the Heroku CLI
3. Login to Heroku:
   ```
   heroku login
   ```
4. Create a new Heroku app:
   ```
   heroku create onthemove-api
   ```
5. Add a Procfile:
   ```
   web: gunicorn run:app
   ```
6. Set environment variables:
   ```
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your_secret_key_here
   heroku config:set JWT_SECRET_KEY=your_jwt_secret_key_here
   heroku config:set SUPABASE_URL=your_supabase_url_here
   heroku config:set SUPABASE_KEY=your_supabase_anon_key_here
   heroku config:set SUPABASE_SERVICE_KEY=your_supabase_service_key_here
   ```
7. Deploy the application:
   ```
   git push heroku main
   ```

## License

This project is licensed under the MIT License. 