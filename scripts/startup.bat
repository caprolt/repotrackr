@echo off
setlocal enabledelayedexpansion

REM RepoTrackr Startup Script for Windows
REM This script sets up and starts the entire RepoTrackr application
REM Supports both Supabase and local database modes

echo ==========================================
echo     RepoTrackr Startup Script
echo ==========================================
echo.

REM Check if we're in the project root
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

REM Detect database mode
echo [INFO] Detecting database mode...
set DB_MODE=local
if exist "backend\.env" (
    findstr /C:"SUPABASE_URL" backend\.env >nul 2>&1
    if not errorlevel 1 (
        findstr /C:"SUPABASE_URL=.*[^ ]" backend\.env >nul 2>&1
        if not errorlevel 1 (
            set DB_MODE=supabase
        )
    )
)
echo [INFO] Detected database mode: %DB_MODE%

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

REM Check Docker only for local mode
if "%DB_MODE%"=="local" (
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker is not installed or not in PATH (required for local database mode)
        pause
        exit /b 1
    )

    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker Compose is not installed or not in PATH (required for local database mode)
        pause
        exit /b 1
    )
)

echo [SUCCESS] All prerequisites are installed

REM Start Docker services only for local mode
if "%DB_MODE%"=="local" (
    echo [INFO] Starting Docker services (PostgreSQL and Redis)...
    
    if not exist "docker-compose.yml" (
        echo [ERROR] docker-compose.yml not found. Make sure you're in the project root directory.
        pause
        exit /b 1
    )
    
    docker-compose up -d postgres redis

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
) else (
    echo [SUCCESS] Using Supabase database - no Docker services needed
)

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

REM Check database mode and provide guidance
if "%DB_MODE%"=="supabase" (
    echo [SUCCESS] Supabase mode detected - using cloud database
) else (
    echo [WARNING] Local database mode detected - make sure Docker services are running
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
echo Database Mode: %DB_MODE%
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
if "%DB_MODE%"=="supabase" (
    echo Database: Supabase (cloud)
    echo   - No local Docker containers needed
    echo   - Database managed in Supabase dashboard
) else (
    echo Database: Local PostgreSQL + Redis
    echo   - Docker containers running locally
    echo   - To stop database: docker-compose down
)
echo.
echo To stop the services, run: scripts\shutdown.bat
echo.
echo Press any key to exit...
pause >nul
