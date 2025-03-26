#!/bin/bash

# CLAI Chat Local Demo Setup
echo "Setting up CLAI Chat for local demo..."

# Build and start containers
echo "Building and starting containers..."
docker-compose up -d --build

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Initialize database
echo "Initializing database..."
docker-compose exec api python -c "from app import app; from utils.db_init import init_db; init_db(app)"

echo "Setup complete! Services are running at:"
echo "- API: http://localhost:5000"
echo "- Admin Dashboard: http://localhost:3000"

echo "Default credentials:"
echo "- Email: admin@clai-chat.com"
echo "- Password: admin123"

echo "To see logs, run: docker-compose logs -f"
echo "To stop the demo, run: docker-compose down"
