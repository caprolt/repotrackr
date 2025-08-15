@echo off
REM RepoTrackr Development Setup Script for Windows

echo 🚀 Setting up RepoTrackr development environment...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Start database and Redis services
echo 📦 Starting database and Redis services...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Backend setup
echo 🐍 Setting up Python backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️ Creating .env file...
    copy .env.example .env
    echo ✅ Created .env file. You may want to review and edit it.
)

REM Initialize Alembic if not already done
if not exist "alembic\versions" (
    echo 🗄️ Initializing database migrations...
    alembic init alembic
    REM Update alembic.ini with correct database URL
    powershell -Command "(Get-Content alembic.ini) -replace 'sqlalchemy.url = driver://user:pass@localhost/dbname', '# This URL will be dynamically set by env.py based on environment variables`nsqlalchemy.url = ' | Set-Content alembic.ini"
)

REM Run database migrations
echo 🗄️ Running database migrations...
alembic upgrade head

cd ..

REM Frontend setup
echo ⚛️ Setting up Next.js frontend...
cd frontend

REM Install dependencies
echo 📦 Installing Node.js dependencies...
npm install

cd ..

echo.
echo ✅ Setup complete!
echo.
echo 🎯 Next steps:
echo 1. Start the backend: cd backend ^&^& venv\Scripts\activate ^&^& python start.py
echo 2. Start the frontend: cd frontend ^&^& npm run dev
echo 3. Open http://localhost:3000 in your browser
echo.
echo 📚 API documentation will be available at http://localhost:8000/api/v1/docs
echo.
echo 🔧 Development commands:
echo   Backend tests: cd backend ^&^& pytest
echo   Frontend tests: cd frontend ^&^& npm test
echo   Format code: cd backend ^&^& black .
echo   Lint code: cd backend ^&^& flake8

pause
