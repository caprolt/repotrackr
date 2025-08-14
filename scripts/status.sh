#!/bin/bash

# RepoTrackr Status Script
# This script checks the status of all RepoTrackr services

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

# Function to check if service is running on port
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_success "$service_name is running on port $port"
        return 0
    else
        print_error "$service_name is not running on port $port"
        return 1
    fi
}

# Function to check Docker services
check_docker_services() {
    print_status "Checking Docker services..."
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found"
        return 1
    fi
    
    if docker-compose ps | grep -q "Up"; then
        print_success "Docker services are running"
        docker-compose ps
        return 0
    else
        print_error "Docker services are not running"
        return 1
    fi
}

# Function to check backend health
check_backend_health() {
    print_status "Checking backend health..."
    
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        print_success "Backend API is healthy"
        return 0
    else
        print_error "Backend API is not responding"
        return 1
    fi
}

# Function to check frontend
check_frontend() {
    print_status "Checking frontend..."
    
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is accessible"
        return 0
    else
        print_error "Frontend is not accessible"
        return 1
    fi
}

# Function to show service URLs
show_urls() {
    echo ""
    echo "Service URLs:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Documentation: http://localhost:8000/api/v1/docs"
    echo ""
}

# Main execution
main() {
    echo "=========================================="
    echo "    RepoTrackr Status Check"
    echo "=========================================="
    echo ""
    
    # Check if we're in the project root
    if [ ! -f "docker-compose.yml" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    local all_services_ok=true
    
    # Check Docker services
    if ! check_docker_services; then
        all_services_ok=false
    fi
    
    echo ""
    
    # Check individual services
    if ! check_port 5432 "PostgreSQL"; then
        all_services_ok=false
    fi
    
    if ! check_port 6379 "Redis"; then
        all_services_ok=false
    fi
    
    if ! check_port 8000 "Backend"; then
        all_services_ok=false
    fi
    
    if ! check_port 3000 "Frontend"; then
        all_services_ok=false
    fi
    
    echo ""
    
    # Check API health
    if ! check_backend_health; then
        all_services_ok=false
    fi
    
    # Check frontend accessibility
    if ! check_frontend; then
        all_services_ok=false
    fi
    
    # Show results
    if [ "$all_services_ok" = true ]; then
        echo ""
        print_success "All RepoTrackr services are running!"
        show_urls
    else
        echo ""
        print_error "Some services are not running properly."
        echo ""
        echo "To start all services, run: ./scripts/startup.sh"
        echo "To stop all services, run: ./scripts/shutdown.sh"
        echo ""
    fi
}

# Run main function
main "$@"
