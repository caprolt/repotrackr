# RepoTrackr Scripts

This directory contains automation scripts for managing the RepoTrackr application.

## 📋 Available Scripts

### 🚀 Startup Scripts

#### `startup.sh` (Linux/macOS)
Comprehensive startup script that:
- Checks prerequisites (Python, Node.js, Docker, Git)
- Verifies port availability
- Starts Docker services (PostgreSQL, Redis)
- Sets up backend (virtual environment, dependencies, migrations)
- Sets up frontend (dependencies)
- Starts backend and frontend servers
- Provides real-time status updates

**Usage:**
```bash
./scripts/startup.sh
```

#### `startup.bat` (Windows)
Windows equivalent of the startup script with the same functionality.

**Usage:**
```cmd
scripts\startup.bat
```

### 🛑 Shutdown Scripts

#### `shutdown.sh` (Linux/macOS)
Gracefully stops all RepoTrackr services:
- Stops backend server
- Stops frontend server
- Stops Docker services
- Cleans up processes and PID files

**Usage:**
```bash
./scripts/shutdown.sh
```

#### `shutdown.bat` (Windows)
Windows equivalent of the shutdown script.

**Usage:**
```cmd
scripts\shutdown.bat
```

### 📊 Status Scripts

#### `status.sh` (Linux/macOS)
Checks the status of all RepoTrackr services:
- Docker services status
- Port availability checks
- Backend health check
- Frontend accessibility check
- Service URLs display

**Usage:**
```bash
./scripts/status.sh
```

#### `status.bat` (Windows)
Windows equivalent of the status script.

**Usage:**
```cmd
scripts\status.bat
```

## 🎯 Quick Start

### For Linux/macOS Users:
```bash
# Start all services
./scripts/startup.sh

# Check status
./scripts/status.sh

# Stop all services
./scripts/shutdown.sh
```

### For Windows Users:
```cmd
# Start all services
scripts\startup.bat

# Check status
scripts\status.bat

# Stop all services
scripts\shutdown.bat
```

## 🔧 What the Scripts Do

### Startup Process:
1. **Prerequisites Check**: Verifies Python 3.9+, Node.js 18+, Docker, Docker Compose, Git
2. **Port Check**: Ensures required ports (8000, 3000, 5432, 6379) are available
3. **Docker Services**: Starts PostgreSQL and Redis containers
4. **Backend Setup**:
   - Creates Python virtual environment
   - Installs dependencies from `requirements.txt`
   - Creates `.env` file from `.env.example`
   - Runs database migrations
5. **Frontend Setup**:
   - Installs Node.js dependencies
6. **Service Startup**:
   - Starts backend server on port 8000
   - Starts frontend development server on port 3000
7. **Health Checks**: Verifies all services are running properly

### Shutdown Process:
1. **Service Termination**: Stops backend and frontend servers
2. **Docker Cleanup**: Stops and removes Docker containers
3. **Process Cleanup**: Kills any remaining processes on service ports
4. **File Cleanup**: Removes PID files and temporary files

### Status Check:
1. **Docker Status**: Checks if containers are running
2. **Port Checks**: Verifies services are listening on correct ports
3. **Health Checks**: Tests API endpoints and frontend accessibility
4. **Summary**: Provides overall status and service URLs

## 📁 Generated Files

The scripts create and manage the following files:

- `logs/` - Directory for log files
  - `backend.log` - Backend server logs
  - `frontend.log` - Frontend server logs
  - `backend.pid` - Backend process ID (Linux/macOS)
  - `frontend.pid` - Frontend process ID (Linux/macOS)

## ⚠️ Important Notes

### Prerequisites:
- **Python 3.9+**: For backend development
- **Node.js 18+**: For frontend development
- **Docker & Docker Compose**: For database and Redis services
- **Git**: For version control
- **curl**: For health checks (usually pre-installed)

### Environment Setup:
- The scripts automatically create `.env` files from `.env.example`
- Review and modify `.env` files as needed for your environment
- Database migrations are run automatically

### Port Requirements:
- **8000**: Backend API server
- **3000**: Frontend development server
- **5432**: PostgreSQL database
- **6379**: Redis cache/queue

### Troubleshooting:
- If services fail to start, check the log files in the `logs/` directory
- Ensure Docker is running before executing the scripts
- Make sure you're in the project root directory when running scripts
- For Windows users, ensure PowerShell or Command Prompt has appropriate permissions

## 🔄 Manual Override

If you need to start services manually:

### Backend:
```bash
cd backend
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.bat  # Windows
python start.py
```

### Frontend:
```bash
cd frontend
npm run dev
```

### Docker Services:
```bash
docker-compose up -d
```

## 📞 Support

If you encounter issues with the scripts:
1. Check the log files in the `logs/` directory
2. Verify all prerequisites are installed
3. Ensure you're running from the project root directory
4. Check that required ports are not in use by other applications
