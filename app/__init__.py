from flask import Flask
from flask_cors import CORS
from app.config import get_config

def create_app(config_class=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register a simple route for testing
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'OnTheMove API is running'}
    
    return app

def register_blueprints(app):
    """Register Flask blueprints."""
    # Import blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.vehicles import vehicles_bp
    from app.routes.locations import locations_bp
    from app.routes.people import people_bp
    from app.routes.trips import trips_bp
    from app.routes.ride_requests import ride_requests_bp
    from app.routes.ratings import ratings_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(vehicles_bp, url_prefix='/api/vehicles')
    app.register_blueprint(locations_bp, url_prefix='/api/locations')
    app.register_blueprint(people_bp, url_prefix='/api/people')
    app.register_blueprint(trips_bp, url_prefix='/api/trips')
    app.register_blueprint(ride_requests_bp, url_prefix='/api/ride-requests')
    app.register_blueprint(ratings_bp, url_prefix='/api/ratings')
    
    # Additional blueprints will be registered here as they are created

def register_error_handlers(app):
    """Register error handlers."""
    @app.errorhandler(400)
    def bad_request(e):
        return {'error': 'Bad Request', 'message': str(e)}, 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return {'error': 'Unauthorized', 'message': str(e)}, 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return {'error': 'Forbidden', 'message': str(e)}, 403
    
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Not Found', 'message': str(e)}, 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return {'error': 'Internal Server Error', 'message': str(e)}, 500
