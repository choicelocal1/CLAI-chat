#!/bin/bash

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running. Please start Docker and try again."
  exit 1
fi

# Set OpenAI API key if provided
if [ -z "$OPENAI_API_KEY" ] && [ -f .env ]; then
  source .env
fi

if [ -z "$OPENAI_API_KEY" ]; then
  echo "Warning: OPENAI_API_KEY environment variable not set. LLM functionality will be limited."
  echo "You can set it by running: export OPENAI_API_KEY=your_api_key"
else
  echo "Using OpenAI API key from environment"
fi

# Build and start services
docker-compose up -d --build

echo "Starting services..."
echo "Waiting for services to initialize..."
sleep 10

# Initialize the database
echo "Initializing database with sample data..."
docker-compose exec api python -c "from app import app; from utils.db_init import init_db; init_db(app)"

echo "================================"
echo "CLAI Chat Demo is now running!"
echo "================================"
echo ""
echo "Access the different components at:"
echo "- API: http://localhost:5000"
echo "- Admin Dashboard: http://localhost:3000"
echo "- Widget Development Server: http://localhost:9000"
echo ""
echo "Admin Login:"
echo "- Email: admin@clai-chat.com"
echo "- Password: admin123"
echo ""
echo "Demo User Login:"
echo "- Email: demo@clai-chat.com"
echo "- Password: demo123"
echo ""
echo "To stop the demo, run: ./stop_demo.sh"
echo "To view logs, run: docker-compose logs -f"
