# Implementation Plan — RepoTrackr (FastAPI + Next.js)

## Milestone 1: Backend MVP (FastAPI)
- [ ] Set up FastAPI project structure
- [ ] Configure Postgres and SQLAlchemy models for `projects`, `tasks`, `progress_snapshots`, `skills`
- [ ] Add `/projects` endpoints (create, list, detail)
- [ ] Implement synchronous repo clone + plan parsing from `docs/plan.md`
- [ ] Parse GitHub-style markdown checkboxes and tables into tasks
- [ ] Compute % complete, counts, and status (green/yellow/red)
- [ ] Store progress snapshot in DB
- [ ] Add CORS middleware for frontend access

## Milestone 2: Frontend MVP (Next.js)
- [ ] Create Next.js app with app router
- [ ] Add dashboard page to list projects with name + status
- [ ] Add project detail page with tasks and progress
- [ ] Add % complete ring or progress bar
- [ ] Add skill chips (placeholder until skills parser ready)

## Milestone 3: Skills Extraction
- [ ] Parse `requirements.txt`, `package.json`, and `Dockerfile`
- [ ] Map raw package names to normalized skill categories
- [ ] Store in `skills` table with source and confidence
- [ ] Display skills in project detail page

## Milestone 4: GitHub Integration
- [ ] Create GitHub App with `contents:read` and `metadata:read`
- [ ] Add `/webhooks/github` endpoint with signature verification
- [ ] Trigger re-parse when plan or manifest files change
- [ ] Record new `progress_snapshot` per webhook event

## Milestone 5: Automation & Background Jobs
- [ ] Add Redis + RQ for async clone/parse tasks
- [ ] Move sync parsing to background jobs
- [ ] Add `/projects/{id}/refresh` to manually enqueue parse

## Milestone 6: UI Polish
- [ ] Add form to create project via frontend
- [ ] Add sparkline/timeline of % complete over time
- [ ] Highlight stale projects (no updates > N days)
- [ ] Add filters and search to dashboard

## Milestone 7: Optional Enhancements
- [ ] Support plan extraction from GitHub Issues or Project boards
- [ ] Multi-repo support for one project
- [ ] LLM-generated project summary from README.md
- [ ] Deploy on Fly.io/Render with HTTPS and domain

---
**Status legend**:  
✅ Done 🔲 To Do

