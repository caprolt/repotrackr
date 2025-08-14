# RepoTrackr — Project Summary

## 🚀 Quick Start

Want to get up and running immediately? Use our automated scripts:

### **Option 1: Automated Scripts (Recommended)**

**For Linux/macOS:**
```bash
# Clone and setup
git clone <repository-url>
cd repotrackr

# Start everything with one command
./scripts/startup.sh
```

**For Windows:**
```cmd
# Clone and setup
git clone <repository-url>
cd repotrackr

# Start everything with one command
scripts\startup.bat
```

### **Option 2: Manual Setup**

```bash
# 1. Clone and setup
git clone <repository-url>
cd repotrackr

# 2. Start infrastructure
docker-compose up -d

# 3. Backend (Terminal 1)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python start.py

# 4. Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs

**Manage services:**
- Check status: `./scripts/status.sh` (Linux/macOS) or `scripts\status.bat` (Windows)
- Stop services: `./scripts/shutdown.sh` (Linux/macOS) or `scripts\shutdown.bat` (Windows)

For detailed setup instructions, see [Section 7: Testing and Running the Application](#7-testing-and-running-the-application).

---

## 1. Overview & Goal

**RepoTrackr** is a lightweight yet automated project tracking system designed for developers managing multiple personal or side projects.  
Its primary goal is to **connect to a project's GitHub repository, locate the implementation plan, parse it for task status, and provide a live view of progress and skills used** — without any manual spreadsheet updates or status reports.

**Core Idea:**  
You add a project with its GitHub repository URL → RepoTrackr scans the repo for a plan file (like `docs/plan.md`) → tasks are parsed and stored → progress is automatically calculated and updated when the repo changes.

This project emphasizes:
- **Automation over manual tracking**
- **Minimal setup** — no complex integrations needed for MVP
- **Developer-first features** — parses code-related files to extract skill/tool usage
- **Visual, central dashboard** for all active projects

---

## 2. Key Features

- **Add Projects** with just a name and GitHub repo URL
- **Plan Parsing** from Markdown checkboxes, Markdown tables, or (future) GitHub Issues/Projects
- **Automatic Progress Calculation** — percentage complete, task counts, and status (green/yellow/red)
- **Skills Extraction** from dependency manifests (`requirements.txt`, `package.json`, `Dockerfile`)
- **Snapshot Timeline** to track how progress changes over time
- **GitHub Webhook Integration** for real-time updates (optional in MVP)
- **Lightweight UI** to see dashboard + project details
- **Expandable Architecture** for multi-repo projects, LLM summaries, and more

---

## 3. Architecture

**Components:**
1. **Frontend (Next.js)**
   - Displays dashboard with all projects, their statuses, and last updated time
   - Project detail view showing:
     - Parsed plan rendered with current statuses
     - Skills/tools chips grouped by category
     - Progress timeline
   - Future: project creation form, search/filter, sparkline charts

2. **Backend API (FastAPI)**
   - REST endpoints for CRUD operations on projects, tasks, skills
   - Endpoint for manual refresh
   - Webhook endpoint for GitHub events
   - CORS-enabled for frontend access
   - Implements business logic for:
     - Parsing plan files
     - Calculating progress and status
     - Storing snapshots

3. **Worker (FastAPI + RQ/Redis)**
   - Handles background jobs for:
     - Cloning repos (shallow clones)
     - Detecting and parsing plan files
     - Extracting skills from manifests
   - Runs parsing asynchronously to avoid blocking API calls

4. **Database (Postgres)**
   - Stores:
     - Projects (name, repo, plan path, status)
     - Tasks (title, status, file path, commit info)
     - Progress Snapshots (percentage, counts, timestamps)
     - Skills (tool name, category, source, confidence)

5. **Queue/Cache (Redis)**
   - Job queue for background parsing
   - Potential caching layer for frequent API responses

---

## 4. Technology Choices

- **Backend**: FastAPI (Python) — chosen for ease of data parsing and strong Python ecosystem for file and text analysis.
- **Frontend**: Next.js (React) — chosen for rich component ecosystem and SSR/ISR support.
- **Database**: PostgreSQL — robust relational DB with JSON support for flexible task and skill metadata.
- **Queue**: Redis + RQ — simple, reliable background processing.
- **Git Integration**: `gitpython` (for repo clones) and GitHub API for metadata/board parsing.
- **Parsing Libraries**: `markdown-it-py` for plan file parsing, `tomli`/`PyYAML` for manifest parsing.

---

## 5. Status Calculation Logic

**Status levels:**
- **Green**: ≥ 70% tasks complete, no blocked items
- **Yellow**: 30–69% complete, ≤ 1 blocked task
- **Red**: < 30% complete, > 1 blocked task, or stale (no updates for N days)

**Progress computation:**
1. Count tasks by status
2. Calculate `% complete = done / (todo + doing + done)`
3. Apply thresholds for color coding
4. Store snapshot in DB for timeline view

---

## 6. Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker and Docker Compose
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd repotrackr
   ```

2. **Start the database and Redis services**
   ```bash
   docker-compose up -d
   ```

3. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env if needed
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the backend server**
   ```bash
   python start.py
   # Or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

7. **Start the frontend development server**
   ```bash
   npm run dev
   ```

8. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/v1/docs

### Development Commands

**Backend:**
```bash
cd backend
# Run tests
pytest

# Format code
black .

# Lint code
flake8

# Run migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

**Frontend:**
```bash
cd frontend
# Run tests
npm test

# Type check
npm run type-check

# Lint
npm run lint
```

---

## 7. Testing and Running the Application

### Prerequisites Check
Before starting, ensure you have the following installed:
- **Python 3.9+**: `python --version`
- **Node.js 18+**: `node --version`
- **Docker & Docker Compose**: `docker --version` and `docker-compose --version`
- **Git**: `git --version`

### Step-by-Step Startup Guide

#### 1. Start Infrastructure Services
```bash
# Start PostgreSQL and Redis containers
docker-compose up -d

# Verify services are running
docker-compose ps
```

#### 2. Backend Setup and Startup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env if needed (database URLs, etc.)

# Run database migrations
alembic upgrade head

# Start the backend server
python start.py
# Or alternatively: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend should be running at:** http://localhost:8000
**API Documentation:** http://localhost:8000/api/v1/docs

#### 3. Frontend Setup and Startup
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

**Frontend should be running at:** http://localhost:3000

#### 4. Verify Everything is Working

1. **Check Backend Health:**
   ```bash
   curl http://localhost:8000/api/v1/health
   # Should return: {"status": "healthy"}
   ```

2. **Check Frontend:**
   - Open http://localhost:3000 in your browser
   - You should see the RepoTrackr dashboard
   - The page should redirect to http://localhost:3000/dashboard

3. **Test API Endpoints:**
   - Visit http://localhost:8000/api/v1/docs for interactive API documentation
   - Try the `/api/v1/projects/` endpoint to see if it returns an empty list

### Development Commands

**Backend Commands:**
```bash
cd backend
# Run tests
pytest

# Format code
black .

# Lint code
flake8

# Run migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Type checking
mypy app/
```

**Frontend Commands:**
```bash
cd frontend
# Run tests
npm test

# Type check
npm run type-check

# Lint
npm run lint

# Build for production
npm run build

# Start production server
npm start
```

### Troubleshooting

#### Common Issues:

1. **Port Already in Use:**
   ```bash
   # Check what's using the port
   lsof -i :8000  # Backend
   lsof -i :3000  # Frontend
   
   # Kill the process or use different ports
   ```

2. **Database Connection Issues:**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps
   
   # Restart services
   docker-compose down
   docker-compose up -d
   ```

3. **Frontend Build Issues:**
   ```bash
   # Clear node modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Backend Import Errors:**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

### Testing the Application

1. **Add a Test Project:**
   - Go to http://localhost:3000
   - Click "Add Project"
   - Fill in project details:
     - Name: "Test Project"
     - Repository URL: "https://github.com/username/test-repo"
     - Plan Path: "docs/plan.md" (default)

2. **Verify API Integration:**
   - Check that the project appears in the dashboard
   - Click "View Details" to see the project detail page
   - Try the "Refresh" button to trigger processing

3. **Test Error Handling:**
   - Try adding a project with an invalid repository URL
   - Verify error messages are displayed properly

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/repotrackr
REDIS_URL=redis://localhost:6379
GITHUB_TOKEN=your_github_token_here
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 8. Roadmap (MVP → v1.0)

**Phase 1: Foundation & Core Infrastructure ✅ COMPLETED**
- ✅ Project setup and environment
- ✅ Database schema with all core tables
- ✅ Basic CRUD API endpoints for projects
- ✅ Development environment with hot reload

**Phase 2: Plan Parsing Engine ✅ COMPLETED**
- ✅ Plan parsing engine
- ✅ Repository integration
- ✅ Markdown parser implementation
- ✅ Progress calculation engine

**Phase 3: Frontend Foundation ✅ COMPLETED**
- ✅ Next.js 14 with App Router
- ✅ Dashboard with project overview
- ✅ Project detail pages with progress visualization
- ✅ API integration and component library
- ✅ Responsive design system

**Phase 4: Skills Extraction (In Progress)**
- Skills extraction from manifests
- Manual refresh API
- Frontend skill display

**v1.0**
- GitHub webhook integration
- Progress timeline chart
- Multi-repo project support
- Hosted deployment

---

## 8. Guiding Principles
- Keep it **minimal** and **extensible**
- Avoid storing full repo code — only parsed metadata
- Automate wherever possible
- Keep status visible and accurate with minimal manual input

---

**Author:** Your Name  
**License:** MIT
