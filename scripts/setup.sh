#!/bin/bash

# RepoTrackr Development Setup Script
set -e

echo "🚀 Setting up RepoTrackr development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start database and Redis services
echo "📦 Starting database and Redis services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
if ! docker-compose ps | grep -q "healthy"; then
    echo "⚠️  Services may not be fully ready. Continuing anyway..."
fi

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env file. You may want to review and edit it."
fi

# Initialize Alembic if not already done
if [ ! -d "alembic/versions" ]; then
    echo "🗄️  Initializing database migrations..."
    alembic init alembic
    # Update alembic.ini with correct database URL
    sed -i 's|sqlalchemy.url = driver://user:pass@localhost/dbname|sqlalchemy.url = postgresql://repotrackr:repotrackr_dev@localhost:5432/repotrackr|' alembic.ini
fi

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

cd ..

# Frontend setup
echo "⚛️  Setting up Next.js frontend..."
cd frontend

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Start the backend: cd backend && source venv/bin/activate && python start.py"
echo "2. Start the frontend: cd frontend && npm run dev"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 API documentation will be available at http://localhost:8000/api/v1/docs"
echo ""
echo "🔧 Development commands:"
echo "  Backend tests: cd backend && pytest"
echo "  Frontend tests: cd frontend && npm test"
echo "  Format code: cd backend && black ."
echo "  Lint code: cd backend && flake8"
