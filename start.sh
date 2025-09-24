#!/bin/bash

echo "Starting Bulk Document Conversion Service..."
echo "=========================================="

# Create necessary directories
mkdir -p uploads outputs temp

# Start the services
echo "Starting services with docker-compose..."
docker-compose up --build

echo "Service started! Access the API at http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
