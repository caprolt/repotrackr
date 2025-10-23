# RepoTrackr 🚀# RepoTrackr — Project Summary



> An automated project tracking system that connects to GitHub repositories, parses implementation plans, and visualizes project progress — all without manual updates.## 🚀 Quick Start



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)Want to get up and running immediately? Use our automated scripts:

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com)

[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)### **Option 1: Automated Scripts (Recommended)**



[Live Demo](#) • [Documentation](./docs) • [Report Bug](https://github.com/caprolt/repotrackr/issues)**For Linux/macOS:**

```bash

---# Clone and setup

git clone <repository-url>

## 🎯 Overviewcd repotrackr



RepoTrackr automatically tracks progress across multiple development projects by parsing Markdown plan files directly from GitHub repositories. It eliminates the tedious task of manual status updates while providing real-time insights into project completion, task breakdown, and technology usage.# Start everything with one command

./scripts/startup.sh

**Key Problem Solved:** As developers, we often work on multiple side projects simultaneously. Keeping track of progress across repos is time-consuming and error-prone. RepoTrackr automates this entirely.```



### ✨ Key Features**For Windows:**

```cmd

- **🔄 Automatic Synchronization** - Connect GitHub repos and auto-parse implementation plans# Clone and setup

- **📊 Visual Dashboard** - See all projects at a glance with progress bars and status indicatorsgit clone <repository-url>

- **✅ Task Tracking** - Parse Markdown checkboxes and tables to extract task statuscd repotrackr

- **🛠️ Skills Detection** - Automatically identify technologies from `package.json`, `requirements.txt`, etc.

- **📈 Progress History** - Timeline snapshots showing how projects evolve over time# Start everything with one command

- **🎨 Clean UI** - Responsive interface built with Next.js and Tailwind CSSscripts\startup.bat

```

---

### **Option 2: Manual Setup**

## 🏗️ Tech Stack

```bash

### Backend# 1. Clone and setup

- **FastAPI** - Modern Python web framework for building APIsgit clone <repository-url>

- **SQLAlchemy** - Async ORM with PostgreSQLcd repotrackr

- **Alembic** - Database migrations

- **Redis + RQ** - Background job processing# 2. Start infrastructure

- **GitPython** - Git repository interactiondocker-compose up -d



### Frontend# 3. Backend (Terminal 1)

- **Next.js 14** - React framework with App Routercd backend

- **TypeScript** - Type-safe developmentpython -m venv venv

- **Tailwind CSS** - Utility-first stylingsource venv/bin/activate  # Windows: venv\Scripts\activate

- **Lucide Icons** - Beautiful icon librarypip install -r requirements.txt

cp .env.example .env

### Infrastructurealembic upgrade head

- **PostgreSQL** - Primary databasepython start.py

- **Redis** - Caching and job queue

- **Docker** - Containerized development# 4. Frontend (Terminal 2)

cd frontend

---npm install

npm run dev

## 🚀 Quick Start```



### Prerequisites**Access the application:**

- **Python 3.9+**- Frontend: http://localhost:3000

- **Node.js 18+**- Backend API: http://localhost:8000

- **Docker & Docker Compose**- API Docs: http://localhost:8000/api/v1/docs

- **Git**

**Manage services:**

### One-Command Setup- Check status: `./scripts/status.sh` (Linux/macOS) or `scripts\status.bat` (Windows)

- Stop services: `./scripts/shutdown.sh` (Linux/macOS) or `scripts\shutdown.bat` (Windows)

**Linux/macOS:**

```bashFor detailed setup instructions, see [Section 7: Testing and Running the Application](#7-testing-and-running-the-application).

git clone https://github.com/caprolt/repotrackr.git

cd repotrackr---

./scripts/startup.sh

```## 1. Overview & Goal



**Windows:****RepoTrackr** is a lightweight yet automated project tracking system designed for developers managing multiple personal or side projects.  

```cmdIts primary goal is to **connect to a project's GitHub repository, locate the implementation plan, parse it for task status, and provide a live view of progress and skills used** — without any manual spreadsheet updates or status reports.

git clone https://github.com/caprolt/repotrackr.git

cd repotrackr**Core Idea:**  

scripts\startup.batYou add a project with its GitHub repository URL → RepoTrackr scans the repo for a plan file (like `docs/plan.md`) → tasks are parsed and stored → progress is automatically calculated and updated when the repo changes.

```

This project emphasizes:

The application will be available at:- **Automation over manual tracking**

- **Frontend:** http://localhost:3000- **Minimal setup** — no complex integrations needed for MVP

- **API:** http://localhost:8000- **Developer-first features** — parses code-related files to extract skill/tool usage

- **API Docs:** http://localhost:8000/api/v1/docs- **Visual, central dashboard** for all active projects



### Manual Setup---



<details>## 2. Key Features

<summary>Click to expand manual setup instructions</summary>

- **Add Projects** with just a name and GitHub repo URL

#### 1. Start Infrastructure- **Plan Parsing** from Markdown checkboxes, Markdown tables, or (future) GitHub Issues/Projects

```bash- **Automatic Progress Calculation** — percentage complete, task counts, and status (green/yellow/red)

docker-compose up -d- **Skills Extraction** from dependency manifests (`requirements.txt`, `package.json`, `Dockerfile`)

```- **Snapshot Timeline** to track how progress changes over time

- **GitHub Webhook Integration** for real-time updates (optional in MVP)

#### 2. Backend Setup- **Lightweight UI** to see dashboard + project details

```bash- **Expandable Architecture** for multi-repo projects, LLM summaries, and more

cd backend

python -m venv venv---

source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt## 3. Architecture

cp .env.example .env

alembic upgrade head**Components:**

python start.py1. **Frontend (Next.js)**

```   - Displays dashboard with all projects, their statuses, and last updated time

   - Project detail view showing:

#### 3. Frontend Setup     - Parsed plan rendered with current statuses

```bash     - Skills/tools chips grouped by category

cd frontend     - Progress timeline

npm install   - Future: project creation form, search/filter, sparkline charts

npm run dev

```2. **Backend API (FastAPI)**

   - REST endpoints for CRUD operations on projects, tasks, skills

</details>   - Endpoint for manual refresh

   - Webhook endpoint for GitHub events

---   - CORS-enabled for frontend access

   - Implements business logic for:

## 📖 Usage     - Parsing plan files

     - Calculating progress and status

### Adding a Project     - Storing snapshots



1. Navigate to the dashboard at `http://localhost:3000`3. **Worker (FastAPI + RQ/Redis)**

2. Click **"Add Project"**   - Handles background jobs for:

3. Enter:     - Cloning repos (shallow clones)

   - **Project Name** - Display name for your project     - Detecting and parsing plan files

   - **Repository URL** - GitHub repository URL     - Extracting skills from manifests

   - **Plan Path** - Path to your plan file (e.g., `docs/plan.md`)   - Runs parsing asynchronously to avoid blocking API calls

4. Click **"Create Project"**

4. **Database (Postgres)**

RepoTrackr will automatically:   - Stores:

- Clone the repository     - Projects (name, repo, plan path, status)

- Parse the plan file     - Tasks (title, status, file path, commit info)

- Extract tasks and their status     - Progress Snapshots (percentage, counts, timestamps)

- Identify technologies used     - Skills (tool name, category, source, confidence)

- Calculate progress metrics

5. **Queue/Cache (Redis)**

### Plan File Format   - Job queue for background parsing

   - Potential caching layer for frequent API responses

RepoTrackr supports Markdown files with checkboxes:

---

```markdown

## Phase 1: Setup## 4. Technology Choices

- [x] Initialize repository

- [x] Setup development environment- **Backend**: FastAPI (Python) — chosen for ease of data parsing and strong Python ecosystem for file and text analysis.

- [ ] Configure CI/CD- **Frontend**: Next.js (React) — chosen for rich component ecosystem and SSR/ISR support.

- **Database**: PostgreSQL — robust relational DB with JSON support for flexible task and skill metadata.

## Phase 2: Backend- **Queue**: Redis + RQ — simple, reliable background processing.

- [ ] Create API endpoints- **Git Integration**: `gitpython` (for repo clones) and GitHub API for metadata/board parsing.

- [~] Implement database models (in progress)- **Parsing Libraries**: `markdown-it-py` for plan file parsing, `tomli`/`PyYAML` for manifest parsing.

- [ ] Write tests

```---



**Status Indicators:**## 5. Status Calculation Logic

- `[x]` - Completed

- `[~]` - In Progress**Status levels:**

- `[ ]` - Todo- **Green**: ≥ 70% tasks complete, no blocked items

- `[!]` - Blocked- **Yellow**: 30–69% complete, ≤ 1 blocked task

- **Red**: < 30% complete, > 1 blocked task, or stale (no updates for N days)

---

**Progress computation:**

## 📁 Project Structure1. Count tasks by status

2. Calculate `% complete = done / (todo + doing + done)`

```3. Apply thresholds for color coding

repotrackr/4. Store snapshot in DB for timeline view

├── backend/              # FastAPI backend

│   ├── app/---

│   │   ├── api/         # API endpoints

│   │   ├── core/        # Configuration## 6. Development Setup

│   │   ├── db/          # Database models

│   │   ├── schemas/     # Pydantic schemas### Prerequisites

│   │   └── services/    # Business logic- Python 3.9+

│   ├── alembic/         # Database migrations- Node.js 18+

│   └── tests/           # Backend tests- Docker and Docker Compose

├── frontend/            # Next.js frontend- Git

│   ├── app/             # App router pages

│   ├── components/      # React components### Quick Start

│   └── lib/             # Utilities & API client

├── docs/                # Documentation1. **Clone the repository**

├── scripts/             # Automation scripts   ```bash

└── docker-compose.yml   # Development infrastructure   git clone <repository-url>

```   cd repotrackr

   ```

---

2. **Start the database and Redis services**

## 🧪 Testing   ```bash

   docker-compose up -d

```bash   ```

# Backend tests

cd backend3. **Set up the backend**

pytest   ```bash

   cd backend

# Frontend tests (when implemented)   python -m venv venv

cd frontend   source venv/bin/activate  # On Windows: venv\Scripts\activate

npm test   pip install -r requirements.txt

```   cp .env.example .env

   # Edit .env if needed

---   ```



## 🛠️ Development4. **Run database migrations**

   ```bash

### Backend Commands   alembic upgrade head

```bash   ```

# Format code

black .5. **Start the backend server**

   ```bash

# Lint   python start.py

flake8   # Or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   ```

# Type checking

mypy app/6. **Set up the frontend**

   ```bash

# Create migration   cd ../frontend

alembic revision --autogenerate -m "description"   npm install

alembic upgrade head   ```

```

7. **Start the frontend development server**

### Frontend Commands   ```bash

```bash   npm run dev

# Type check   ```

npm run type-check

8. **Access the application**

# Lint   - Frontend: http://localhost:3000

npm run lint   - Backend API: http://localhost:8000

   - API Documentation: http://localhost:8000/api/v1/docs

# Build

npm run build### Development Commands

```

**Backend:**

---```bash

cd backend

## 🗺️ Roadmap# Run tests

pytest

- [x] Core project tracking

- [x] Markdown plan parsing# Format code

- [x] Skills extractionblack .

- [x] Progress visualization

- [ ] GitHub webhook integration# Lint code

- [ ] Multi-repo project supportflake8

- [ ] Custom status labels

- [ ] Export reports (PDF/CSV)# Run migrations

- [ ] Team collaboration featuresalembic revision --autogenerate -m "description"

- [ ] AI-powered insightsalembic upgrade head

```

---

**Frontend:**

## 🤝 Contributing```bash

cd frontend

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.# Run tests

npm test

1. Fork the repository

2. Create your feature branch (`git checkout -b feature/amazing-feature`)# Type check

3. Commit your changes (`git commit -m 'Add amazing feature'`)npm run type-check

4. Push to the branch (`git push origin feature/amazing-feature`)

5. Open a Pull Request# Lint

npm run lint

---```



## 📄 License---



This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.## 7. Testing and Running the Application



---### Prerequisites Check

Before starting, ensure you have the following installed:

## 👤 Author- **Python 3.9+**: `python --version`

- **Node.js 18+**: `node --version`

**Tanner Caprolt**- **Docker & Docker Compose**: `docker --version` and `docker-compose --version`

- **Git**: `git --version`

- GitHub: [@caprolt](https://github.com/caprolt)

- Portfolio: [Your Portfolio URL]### Step-by-Step Startup Guide

- LinkedIn: [Your LinkedIn URL]

#### 1. Start Infrastructure Services

---```bash

# Start PostgreSQL and Redis containers

## 🙏 Acknowledgmentsdocker-compose up -d



- Built as a portfolio project demonstrating full-stack development skills# Verify services are running

- Inspired by the need for better personal project managementdocker-compose ps

- Uses modern best practices for Python and TypeScript development```



---#### 2. Backend Setup and Startup

```bash

**⭐ If you find this project useful, please consider giving it a star!**# Navigate to backend directory

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
