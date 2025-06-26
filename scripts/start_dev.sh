#!/bin/bash

# Development startup script for Soft Skill Practice Service

echo "🚀 Starting Soft Skill Practice Service Development Environment"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update the configuration if needed."
fi

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if database is ready
echo "🔍 Checking database connection..."
until docker-compose exec -T postgres pg_isready -U postgres; do
    echo "Waiting for database..."
    sleep 2
done

echo "✅ Database is ready!"

# Populate initial data
echo "📚 Populating initial data..."
docker-compose exec api python scripts/populate_data.py

# Show service status
echo "📊 Service Status:"
docker-compose ps

# Show useful URLs
echo ""
echo "🌐 Service URLs:"
echo "  • API Documentation (Swagger): http://localhost:8000/docs"
echo "  • API Documentation (ReDoc): http://localhost:8000/redoc"
echo "  • Health Check: http://localhost:8000/health/"
echo "  • PostgreSQL: localhost:5432 (postgres/postgres)"
echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📝 Useful commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart API: docker-compose restart api"
echo "  • Run tests: docker-compose exec api pytest tests/"
