@echo off
setlocal enabledelayedexpansion

REM RepoTrackr Shutdown Script for Windows
REM This script stops all RepoTrackr services

echo ==========================================
echo     RepoTrackr Shutdown Script
echo ==========================================
echo.

REM Check if we're in the project root
if not exist "docker-compose.yml" (
    echo [ERROR] Please run this script from the project root directory.
    pause
    exit /b 1
)

echo [INFO] Stopping backend server...

REM Kill backend processes
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    if not "%%a"=="0" (
        echo [INFO] Killing backend process PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

echo [SUCCESS] Backend server stopped

echo [INFO] Stopping frontend server...

REM Kill frontend processes
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    if not "%%a"=="0" (
        echo [INFO] Killing frontend process PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

echo [SUCCESS] Frontend server stopped

echo [INFO] Stopping Docker services...
docker-compose down

echo [SUCCESS] Docker services stopped

echo [INFO] Cleaning up...

REM Kill any remaining processes on our ports
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5432') do (
    if not "%%a"=="0" (
        echo [INFO] Killing PostgreSQL process PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :6379') do (
    if not "%%a"=="0" (
        echo [INFO] Killing Redis process PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Remove PID files if they exist
if exist "logs\backend.pid" del logs\backend.pid
if exist "logs\frontend.pid" del logs\frontend.pid

echo [SUCCESS] Cleanup complete

echo.
echo [SUCCESS] All RepoTrackr services have been stopped!
echo.
pause
