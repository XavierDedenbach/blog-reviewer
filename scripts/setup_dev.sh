#!/bin/bash

# Blog Reviewer Development Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Blog Reviewer development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Development Environment Variables
ENVIRONMENT=development

# MongoDB
MONGODB_URI=mongodb://admin:password123@localhost:27017/blog_reviewer

# API Keys (replace with your actual keys)
OPENROUTER_API_KEY=your_openrouter_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
GROQ_API_KEY=your_groq_api_key_here
BRAVE_API_KEY=your_brave_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here

# Opik MCP (monitoring server)
OPIK_SERVER=http://localhost:7000
EOF
    echo "✅ .env file created. Please update it with your actual API keys."
else
    echo "✅ .env file already exists."
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🔧 Installing development dependencies..."
pip install pytest pytest-asyncio pytest-mock pytest-cov factory-boy faker black isort flake8 mypy

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d mongodb

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
until docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    echo "   Waiting for MongoDB..."
    sleep 2
done

echo "✅ MongoDB is ready!"

# Run initial tests to verify setup
echo "🧪 Running initial tests..."
pytest --collect-only

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your actual API keys"
echo "2. Run 'docker-compose up' to start all services"
echo "3. Run 'pytest' to run tests"
echo "4. Run 'python -m uvicorn api.main:app --reload' to start the API server"
echo ""
echo "Services:"
echo "- API Server: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- MongoDB: localhost:27017"
echo "- Mongo Express: http://localhost:8081 (admin/password123)"
echo ""
