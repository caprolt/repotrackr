# Implementation Plan — RepoTrackr (FastAPI + Next.js)

## Milestone 1: Backend MVP (FastAPI)
- [x] Set up FastAPI project structure
- [x] Configure Postgres and SQLAlchemy models for `projects`, `tasks`, `progress_snapshots`, `skills`
- [x] Add `/projects` endpoints (create, list, detail)
- [x] Implement synchronous repo clone + plan parsing from `docs/plan.md`
- [x] Parse GitHub-style markdown checkboxes and tables into tasks
- [x] Compute % complete, counts, and status (green/yellow/red)
- [x] Store progress snapshot in DB
- [x] Add CORS middleware for frontend access

## Milestone 2: Frontend MVP (Next.js)
- [x] Create Next.js app with app router
- [x] Add dashboard page to list projects with name + status
- [x] Add project detail page with tasks and progress
- [x] Add % complete ring or progress bar
- [x] Add skill chips (placeholder until skills parser ready)

## Milestone 3: Skills Extraction
- [x] Parse `requirements.txt`, `package.json`, and `Dockerfile`
- [x] Map raw package names to normalized skill categories
- [x] Store in `skills` table with source and confidence
- [x] Display skills in project detail page

## Milestone 4: GitHub Integration
- [ ] Create GitHub App with `contents:read` and `metadata:read`
- [ ] Add `/webhooks/github` endpoint with signature verification
- [ ] Trigger re-parse when plan or manifest files change
- [ ] Record new `progress_snapshot` per webhook event

## Milestone 5: Automation & Background Jobs
- [x] Add Redis + RQ for async clone/parse tasks
- [x] Move sync parsing to background jobs
- [x] Add `/projects/{id}/refresh` to manually enqueue parse

## Milestone 6: UI Polish
- [x] Add form to create project via frontend
- [ ] Add sparkline/timeline of % complete over time
- [ ] Highlight stale projects (no updates > N days)
- [ ] Add filters and search to dashboard

## Milestone 7: Deployment & Infrastructure
- [x] Fix Railway deployment issues (database connection during build)
- [x] Add retry logic for database migrations
- [x] Implement proper health checks
- [x] Create comprehensive troubleshooting guide
- [x] Add database connection testing
- [ ] Deploy on Railway with HTTPS and domain
- [ ] Set up CI/CD pipeline

## Milestone 8: Optional Enhancements
- [ ] Support plan extraction from GitHub Issues or Project boards
- [ ] Multi-repo support for one project
- [ ] LLM-generated project summary from README.md
- [ ] Advanced monitoring and logging

---
**Status legend**:  
✅ Done 🔲 To Do

## Recent Fixes (Railway Deployment)

### Database Connection Issues
- **Problem**: Alembic migrations running during Docker build when `DATABASE_URL` not available
- **Solution**: Moved migrations to runtime startup with retry logic
- **Files Modified**: `Dockerfile`, `start.py`, `railway.toml`

### Startup Reliability
- **Problem**: Database not ready when app starts
- **Solution**: Added exponential backoff retry logic
- **Files Modified**: `start.py`

### Health Checks
- **Problem**: Railway health checks failing
- **Solution**: Enhanced `/health` endpoint with database status
- **Files Modified**: `app/main.py`

### Diagnostics
- **Problem**: Difficult to debug deployment issues
- **Solution**: Added comprehensive diagnostic scripts
- **Files Added**: `test_db_connection.py`, `RAILWAY_TROUBLESHOOTING.md`

