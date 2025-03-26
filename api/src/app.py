from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config.config import Config
from models.db import db
from routes import register_routes
from services.socket_service import socketio

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    CORS(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register routes
    register_routes(app)
    
    # Health check route
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
