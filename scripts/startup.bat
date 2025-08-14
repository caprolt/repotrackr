@echo off
setlocal enabledelayedexpansion

REM RepoTrackr Startup Script for Windows
REM This script sets up and starts the entire RepoTrackr application

echo ==========================================
echo     RepoTrackr Startup Script
echo ==========================================
echo.

REM Check if we're in the project root
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found. Make sure you're in the project root directory.
    pause
    exit /b 1
)

if not exist "backend" (
    echo [ERROR] backend directory not found. Make sure you're in the project root directory.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] frontend directory not found. Make sure you're in the project root directory.
    pause
    exit /b 1
)

REM Create logs directory
if not exist "logs" mkdir logs

echo [INFO] Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    pause
    exit /b 1
)

REM Check Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed or not in PATH
    pause
    exit /b 1
)

echo [SUCCESS] All prerequisites are installed

echo [INFO] Starting Docker services (PostgreSQL and Redis)...
docker-compose up -d

REM Wait for services to be ready
echo [INFO] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo [ERROR] Failed to start Docker services
    docker-compose logs
    pause
    exit /b 1
)

echo [SUCCESS] Docker services are running

echo [INFO] Setting up backend...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

REM Setup environment file
if not exist ".env" (
    echo [INFO] Creating .env file...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [WARNING] Created .env from .env.example. Please review and modify if needed.
    ) else (
        echo [WARNING] No .env.example found. You may need to create .env manually.
    )
)

REM Run database migrations
echo [INFO] Running database migrations...
alembic upgrade head

echo [SUCCESS] Backend setup complete
cd ..

echo [INFO] Setting up frontend...
cd frontend

REM Install dependencies
echo [INFO] Installing Node.js dependencies...
npm install

echo [SUCCESS] Frontend setup complete
cd ..

echo [INFO] Starting backend server...
cd backend

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the server in background
start /B python start.py > ..\logs\backend.log 2>&1

REM Wait a moment for server to start
timeout /t 3 /nobreak >nul

REM Check if server is running
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to start backend server
    pause
    exit /b 1
)

echo [SUCCESS] Backend server is running
cd ..

echo [INFO] Starting frontend server...
cd frontend

REM Start the development server in background
start /B npm run dev > ..\logs\frontend.log 2>&1

REM Wait a moment for server to start
timeout /t 5 /nobreak >nul

REM Check if server is running
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Frontend server may still be starting up...
) else (
    echo [SUCCESS] Frontend server is running
)

cd ..

echo.
echo [SUCCESS] RepoTrackr startup complete!
echo.
echo Services are running at:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - API Documentation: http://localhost:8000/api/v1/docs
echo.
echo Log files:
echo   - Backend: logs\backend.log
echo   - Frontend: logs\frontend.log
echo.
echo To stop the services, run: scripts\shutdown.bat
echo.
echo Press any key to exit...
pause >nul
