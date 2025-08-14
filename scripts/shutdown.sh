#!/bin/bash

# RepoTrackr Shutdown Script
# This script stops all RepoTrackr services

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

# Function to stop backend server
stop_backend() {
    print_status "Stopping backend server..."
    
    if [ -f "logs/backend.pid" ]; then
        local pid=$(cat logs/backend.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_success "Backend server stopped (PID: $pid)"
        else
            print_warning "Backend server was not running"
        fi
        rm -f logs/backend.pid
    else
        print_warning "No backend PID file found"
    fi
}

# Function to stop frontend server
stop_frontend() {
    print_status "Stopping frontend server..."
    
    if [ -f "logs/frontend.pid" ]; then
        local pid=$(cat logs/frontend.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_success "Frontend server stopped (PID: $pid)"
        else
            print_warning "Frontend server was not running"
        fi
        rm -f logs/frontend.pid
    else
        print_warning "No frontend PID file found"
    fi
}

# Function to stop Docker services
stop_docker_services() {
    print_status "Stopping Docker services..."
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
        print_success "Docker services stopped"
    else
        print_warning "docker-compose.yml not found"
    fi
}

# Function to kill processes by port
kill_by_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        print_status "Killing processes on port $port..."
        echo $pids | xargs kill -9
        print_success "Processes on port $port killed"
    fi
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    
    # Kill any remaining processes on our ports
    kill_by_port 8000  # Backend
    kill_by_port 3000  # Frontend
    kill_by_port 5432  # PostgreSQL
    kill_by_port 6379  # Redis
    
    # Remove PID files
    rm -f logs/backend.pid logs/frontend.pid
    
    print_success "Cleanup complete"
}

# Main execution
main() {
    echo "=========================================="
    echo "    RepoTrackr Shutdown Script"
    echo "=========================================="
    echo ""
    
    # Check if we're in the project root
    if [ ! -f "docker-compose.yml" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Stop services
    stop_backend
    stop_frontend
    stop_docker_services
    cleanup
    
    echo ""
    print_success "All RepoTrackr services have been stopped!"
    echo ""
}

# Run main function
main "$@"
