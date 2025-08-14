#!/bin/bash

# RepoTrackr Startup Script
# This script sets up and starts the entire RepoTrackr application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    if ! command_exists python3; then
        missing_deps+=("Python 3.9+")
    fi
    
    if ! command_exists node; then
        missing_deps+=("Node.js 18+")
    fi
    
    if ! command_exists docker; then
        missing_deps+=("Docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("Docker Compose")
    fi
    
    if ! command_exists git; then
        missing_deps+=("Git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        echo ""
        echo "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to check if ports are available
check_ports() {
    print_status "Checking if required ports are available..."
    
    local ports=("8000" "3000" "5432" "6379")
    local occupied_ports=()
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            occupied_ports+=("$port")
        fi
    done
    
    if [ ${#occupied_ports[@]} -ne 0 ]; then
        print_warning "The following ports are already in use:"
        for port in "${occupied_ports[@]}"; do
            echo "  - Port $port"
        done
        echo ""
        echo "Please stop the services using these ports or modify the configuration."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "Ports are available"
}

# Function to start Docker services
start_docker_services() {
    print_status "Starting Docker services (PostgreSQL and Redis)..."
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found. Make sure you're in the project root directory."
        exit 1
    fi
    
    # Start services in detached mode
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Failed to start Docker services"
        docker-compose logs
        exit 1
    fi
    
    print_success "Docker services are running"
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source ../backend/venv/Scripts/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Setup environment file
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Created .env from .env.example. Please review and modify if needed."
        else
            print_warning "No .env.example found. You may need to create .env manually."
        fi
    fi
    
    # Run database migrations
    print_status "Running database migrations..."
    alembic upgrade head
    
    print_success "Backend setup complete"
    cd ..
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    print_success "Frontend setup complete"
    cd ..
}

# Function to start backend server
start_backend() {
    print_status "Starting backend server..."
    
    cd backend
    
    # Activate virtual environment
    source ../backend/venv/Scripts/activate
    
    # Start the server in background
    nohup python start.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Wait a moment for server to start
    sleep 3
    
    # Check if server is running
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        print_success "Backend server is running (PID: $BACKEND_PID)"
        echo $BACKEND_PID > ../logs/backend.pid
    else
        print_error "Failed to start backend server"
        exit 1
    fi
    
    cd ..
}

# Function to start frontend server
start_frontend() {
    print_status "Starting frontend server..."
    
    cd frontend
    
    # Start the development server in background
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Wait a moment for server to start
    sleep 5
    
    # Check if server is running
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend server is running (PID: $FRONTEND_PID)"
        echo $FRONTEND_PID > ../logs/frontend.pid
    else
        print_warning "Frontend server may still be starting up..."
    fi
    
    cd ..
}

# Function to create logs directory
create_logs_directory() {
    if [ ! -d "logs" ]; then
        mkdir -p logs
    fi
}

# Function to show final status
show_status() {
    echo ""
    print_success "RepoTrackr startup complete!"
    echo ""
    echo "Services are running at:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Documentation: http://localhost:8000/api/v1/docs"
    echo ""
    echo "Log files:"
    echo "  - Backend: logs/backend.log"
    echo "  - Frontend: logs/frontend.log"
    echo ""
    echo "To stop the services, run: ./scripts/shutdown.sh"
    echo ""
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
}

# Set up trap for cleanup
trap cleanup EXIT

# Main execution
main() {
    echo "=========================================="
    echo "    RepoTrackr Startup Script"
    echo "=========================================="
    echo ""
    
    # Check if we're in the project root
    if [ ! -f "docker-compose.yml" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Run setup steps
    check_prerequisites
    check_ports
    create_logs_directory
    start_docker_services
    setup_backend
    setup_frontend
    start_backend
    start_frontend
    
    # Show final status
    show_status
    
    # Keep script running to maintain background processes
    print_status "Press Ctrl+C to stop all services"
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"
