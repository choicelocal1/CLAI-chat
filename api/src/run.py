from app import app, socketio
from utils.db_init import init_db

if __name__ == '__main__':
    # Initialize database with required initial data
    init_db(app)
    
    # Run the application with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
