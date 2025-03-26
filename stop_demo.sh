#!/bin/bash

echo "Stopping CLAI Chat Demo..."
docker-compose down

echo "Demo stopped. Data is preserved."
echo "To restart the demo, run: ./run_demo.sh"
