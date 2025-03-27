from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# Configuration directly in app.py for simplicity
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/clai_chat')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Apply CORS
CORS(app)

# Simple socketio mock
class MockSocketIO:
    def __init__(self):
        pass
    
    def run(self, app, host='0.0.0.0', port=5000, debug=False):
        app.run(host=host, port=port, debug=debug)

socketio = MockSocketIO()

@app.route('/')
def index():
    return jsonify({"message": "Welcome to CLAI Chat API"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
