@echo off
setlocal enabledelayedexpansion

REM RepoTrackr Status Script for Windows
REM This script checks the status of all RepoTrackr services

echo ==========================================
echo     RepoTrackr Status Check
echo ==========================================
echo.

REM Check if we're in the project root
if not exist "docker-compose.yml" (
    echo [ERROR] Please run this script from the project root directory.
    pause
    exit /b 1
)

set all_services_ok=true

echo [INFO] Checking Docker services...
if docker-compose ps | findstr "Up" >nul (
    echo [SUCCESS] Docker services are running
    docker-compose ps
) else (
    echo [ERROR] Docker services are not running
    set all_services_ok=false
)

echo.

REM Check individual ports
echo [INFO] Checking service ports...

REM Check PostgreSQL
netstat -an | findstr :5432 >nul
if errorlevel 1 (
    echo [ERROR] PostgreSQL is not running on port 5432
    set all_services_ok=false
) else (
    echo [SUCCESS] PostgreSQL is running on port 5432
)

REM Check Redis
netstat -an | findstr :6379 >nul
if errorlevel 1 (
    echo [ERROR] Redis is not running on port 6379
    set all_services_ok=false
) else (
    echo [SUCCESS] Redis is running on port 6379
)

REM Check Backend
netstat -an | findstr :8000 >nul
if errorlevel 1 (
    echo [ERROR] Backend is not running on port 8000
    set all_services_ok=false
) else (
    echo [SUCCESS] Backend is running on port 8000
)

REM Check Frontend
netstat -an | findstr :3000 >nul
if errorlevel 1 (
    echo [ERROR] Frontend is not running on port 3000
    set all_services_ok=false
) else (
    echo [SUCCESS] Frontend is running on port 3000
)

echo.

echo [INFO] Checking backend health...
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend API is not responding
    set all_services_ok=false
) else (
    echo [SUCCESS] Backend API is healthy
)

echo [INFO] Checking frontend...
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Frontend is not accessible
    set all_services_ok=false
) else (
    echo [SUCCESS] Frontend is accessible
)

echo.

REM Show results
if "%all_services_ok%"=="true" (
    echo [SUCCESS] All RepoTrackr services are running!
    echo.
    echo Service URLs:
    echo   - Frontend: http://localhost:3000
    echo   - Backend API: http://localhost:8000
    echo   - API Documentation: http://localhost:8000/api/v1/docs
    echo.
) else (
    echo [ERROR] Some services are not running properly.
    echo.
    echo To start all services, run: scripts\startup.bat
    echo To stop all services, run: scripts\shutdown.bat
    echo.
)

pause
