# Technical Plan — RepoTrackr

## Project Overview
RepoTrackr is an automated project tracking system that connects to GitHub repositories, parses implementation plans, and provides real-time progress visualization with skill extraction capabilities.

## Architecture Summary
- **Frontend**: Next.js (React) with App Router
- **Backend**: FastAPI (Python) with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Queue**: Redis + RQ for background processing
- **Git Integration**: gitpython + GitHub API
- **Parsing**: markdown-it-py, PyYAML, tomli

---

## Phase 1: Foundation & Core Infrastructure (Weeks 1-2)

### Phase 1.1: Project Setup & Environment
- [ ] Initialize FastAPI project structure with proper organization
- [ ] Set up PostgreSQL database with Docker Compose
- [ ] Configure SQLAlchemy with async support
- [ ] Set up Redis for future queue implementation
- [ ] Create development environment with hot reload
- [ ] Set up linting (black, flake8) and testing (pytest) infrastructure
- [ ] Initialize Next.js app with TypeScript and App Router
- [ ] Configure Tailwind CSS for styling

### Phase 1.2: Database Schema Design
- [ ] Design and implement `projects` table:
  - `id` (UUID, primary key)
  - `name` (VARCHAR, required)
  - `repo_url` (VARCHAR, required, unique)
  - `plan_path` (VARCHAR, default: 'docs/plan.md')
  - `status` (ENUM: 'green', 'yellow', 'red')
  - `last_updated` (TIMESTAMP)
  - `created_at` (TIMESTAMP)
- [ ] Design and implement `tasks` table:
  - `id` (UUID, primary key)
  - `project_id` (UUID, foreign key)
  - `title` (TEXT, required)
  - `status` (ENUM: 'todo', 'doing', 'done', 'blocked')
  - `file_path` (VARCHAR)
  - `line_number` (INTEGER)
  - `commit_hash` (VARCHAR)
  - `created_at` (TIMESTAMP)
- [ ] Design and implement `progress_snapshots` table:
  - `id` (UUID, primary key)
  - `project_id` (UUID, foreign key)
  - `percentage_complete` (DECIMAL)
  - `tasks_total` (INTEGER)
  - `tasks_done` (INTEGER)
  - `tasks_doing` (INTEGER)
  - `tasks_todo` (INTEGER)
  - `tasks_blocked` (INTEGER)
  - `created_at` (TIMESTAMP)
- [ ] Design and implement `skills` table:
  - `id` (UUID, primary key)
  - `project_id` (UUID, foreign key)
  - `name` (VARCHAR, required)
  - `category` (VARCHAR) - e.g., 'language', 'framework', 'tool'
  - `source` (VARCHAR) - e.g., 'requirements.txt', 'package.json'
  - `confidence` (DECIMAL, 0-1)
  - `created_at` (TIMESTAMP)

### Phase 1.3: Core API Endpoints
- [ ] Implement `/projects` endpoints:
  - `POST /projects` - Create new project
  - `GET /projects` - List all projects with pagination
  - `GET /projects/{id}` - Get project details
  - `DELETE /projects/{id}` - Delete project
- [ ] Add CORS middleware configuration
- [ ] Implement basic error handling and validation
- [ ] Add request/response models with Pydantic

---

## Phase 2: Plan Parsing Engine (Weeks 3-4)

### Phase 2.1: Repository Integration
- [ ] Implement GitPython integration for repository cloning
- [ ] Add shallow clone functionality for performance
- [ ] Create repository management service
- [ ] Implement file discovery logic for plan files
- [ ] Add support for multiple plan file locations:
  - `docs/plan.md` (primary)
  - `plan.md` (fallback)
  - `README.md` (with plan section detection)

### Phase 2.2: Markdown Parser Implementation
- [ ] Implement markdown-it-py integration
- [ ] Create checkbox parser for GitHub-style task lists:
  - `- [ ] Task` → status: 'todo'
  - `- [x] Task` → status: 'done'
  - `- [~] Task` → status: 'doing'
  - `- [!] Task` → status: 'blocked'
- [ ] Implement table parser for structured task lists
- [ ] Add support for nested task structures
- [ ] Create task extraction service with validation

### Phase 2.3: Progress Calculation Engine
- [ ] Implement status calculation logic:
  - Green: ≥ 70% complete, no blocked items
  - Yellow: 30-69% complete, ≤ 1 blocked task
  - Red: < 30% complete, > 1 blocked task, or stale
- [ ] Create progress computation service
- [ ] Implement snapshot creation and storage
- [ ] Add stale project detection (configurable threshold)

### Phase 2.4: Synchronous Processing Pipeline
- [ ] Create unified processing pipeline:
  1. Clone repository
  2. Discover plan file
  3. Parse tasks
  4. Calculate progress
  5. Store snapshot
- [ ] Add comprehensive error handling
- [ ] Implement retry logic for network failures
- [ ] Add processing status tracking

---

## Phase 3: Frontend Foundation (Weeks 5-6)

### Phase 3.1: Next.js App Structure
- [ ] Set up Next.js 14 with App Router
- [ ] Configure TypeScript with strict mode
- [ ] Set up Tailwind CSS with custom design system
- [ ] Create component library structure
- [ ] Implement responsive layout components
- [ ] Add dark/light mode support

### Phase 3.2: Dashboard Implementation
- [ ] Create dashboard page (`/app/dashboard/page.tsx`)
- [ ] Implement project card component with:
  - Project name and status indicator
  - Progress percentage display
  - Last updated timestamp
  - Quick action buttons
- [ ] Add project grid/list view toggle
- [ ] Implement loading states and error handling
- [ ] Add empty state for no projects

### Phase 3.3: Project Detail Page
- [ ] Create project detail page (`/app/projects/[id]/page.tsx`)
- [ ] Implement task list component with:
  - Checkbox status indicators
  - Task titles and descriptions
  - File path and line number display
- [ ] Add progress visualization:
  - Circular progress indicator
  - Progress bar with color coding
  - Task count breakdown
- [ ] Create project metadata display
- [ ] Add refresh button for manual updates

### Phase 3.4: API Integration
- [ ] Create API client with fetch/axios
- [ ] Implement data fetching with React Query/SWR
- [ ] Add optimistic updates for better UX
- [ ] Create error boundary components
- [ ] Implement loading skeletons

---

## Phase 4: Skills Extraction System (Weeks 7-8)

### Phase 4.1: Manifest File Parsing
- [ ] Implement `requirements.txt` parser:
  - Extract package names and versions
  - Handle comments and empty lines
  - Support for version specifiers
- [ ] Implement `package.json` parser:
  - Extract dependencies and devDependencies
  - Handle nested package structures
  - Parse scripts for tool detection
- [ ] Implement `Dockerfile` parser:
  - Extract base images
  - Parse RUN commands for tool detection
  - Handle multi-stage builds
- [ ] Add support for additional files:
  - `pyproject.toml`
  - `Cargo.toml`
  - `go.mod`

### Phase 4.2: Skill Categorization Engine
- [ ] Create skill mapping database:
  - Language detection (Python, JavaScript, Rust, Go)
  - Framework categorization (React, Django, FastAPI)
  - Tool classification (Docker, Git, CI/CD)
- [ ] Implement confidence scoring algorithm
- [ ] Add skill normalization (case-insensitive matching)
- [ ] Create skill deduplication logic
- [ ] Add custom skill category support

### Phase 4.3: Skills Display Integration
- [ ] Update project detail page with skills section
- [ ] Create skill chip components with categories
- [ ] Implement skill filtering and sorting
- [ ] Add skill confidence indicators
- [ ] Create skills overview on dashboard

---

## Phase 5: Background Processing & Automation (Weeks 9-10)

### Phase 5.1: Redis Queue Integration
- [ ] Set up Redis with RQ (Redis Queue)
- [ ] Create worker process configuration
- [ ] Implement job serialization/deserialization
- [ ] Add job status tracking and monitoring
- [ ] Create job retry and failure handling

### Phase 5.2: Asynchronous Processing
- [ ] Move repository cloning to background jobs
- [ ] Implement plan parsing as async tasks
- [ ] Add skills extraction to background pipeline
- [ ] Create job queue management endpoints
- [ ] Add job progress tracking

### Phase 5.3: Manual Refresh System
- [ ] Implement `/projects/{id}/refresh` endpoint
- [ ] Add refresh button to frontend
- [ ] Create refresh status indicators
- [ ] Implement refresh rate limiting
- [ ] Add refresh history tracking

---

## Phase 6: GitHub Integration & Webhooks (Weeks 11-12)

### Phase 6.1: GitHub App Setup
- [ ] Create GitHub App with required permissions:
  - `contents:read` for file access
  - `metadata:read` for repository info
- [ ] Configure webhook endpoints
- [ ] Implement app installation flow
- [ ] Add repository access validation

### Phase 6.2: Webhook Implementation
- [ ] Create `/webhooks/github` endpoint
- [ ] Implement webhook signature verification
- [ ] Handle relevant GitHub events:
  - `push` events for plan file changes
  - `pull_request` events for review tracking
  - `issues` events for issue-based planning
- [ ] Add webhook event filtering and processing
- [ ] Implement webhook retry logic

### Phase 6.3: Real-time Updates
- [ ] Trigger background jobs on webhook events
- [ ] Update project status automatically
- [ ] Create new progress snapshots
- [ ] Add webhook event logging
- [ ] Implement webhook health monitoring

---

## Phase 7: UI Enhancement & Polish (Weeks 13-14)

### Phase 7.1: Project Creation Flow
- [ ] Create project creation form component
- [ ] Add form validation and error handling
- [ ] Implement repository URL validation
- [ ] Add plan file path customization
- [ ] Create onboarding flow for new users

### Phase 7.2: Progress Timeline Visualization
- [ ] Implement progress timeline chart component
- [ ] Add sparkline charts for quick progress overview
- [ ] Create historical progress comparison
- [ ] Add trend analysis and predictions
- [ ] Implement interactive chart controls

### Phase 7.3: Advanced Dashboard Features
- [ ] Add project search and filtering
- [ ] Implement project sorting options
- [ ] Create project status overview cards
- [ ] Add bulk operations for multiple projects
- [ ] Implement dashboard customization options

### Phase 7.4: Stale Project Management
- [ ] Add stale project detection and highlighting
- [ ] Implement stale project notifications
- [ ] Create project health indicators
- [ ] Add project archiving functionality
- [ ] Implement project activity tracking

---

## Phase 8: Advanced Features & Optimization (Weeks 15-16)

### Phase 8.1: Multi-repo Project Support
- [ ] Extend project model for multiple repositories
- [ ] Implement cross-repo progress aggregation
- [ ] Create unified project view for multi-repo projects
- [ ] Add repository relationship management
- [ ] Implement cross-repo skill consolidation

### Phase 8.2: GitHub Issues/Projects Integration
- [ ] Add GitHub Issues parser for task extraction
- [ ] Implement GitHub Projects board integration
- [ ] Create issue-to-task mapping logic
- [ ] Add issue status synchronization
- [ ] Implement issue-based progress tracking

### Phase 8.3: Performance Optimization
- [ ] Implement database query optimization
- [ ] Add Redis caching for frequent queries
- [ ] Optimize frontend bundle size
- [ ] Implement lazy loading for large datasets
- [ ] Add database indexing for performance

### Phase 8.4: Analytics & Insights
- [ ] Create project analytics dashboard
- [ ] Implement skill usage analytics
- [ ] Add progress trend analysis
- [ ] Create project comparison features
- [ ] Implement export functionality

---

## Phase 9: Deployment & Production (Weeks 17-18)

### Phase 9.1: Production Environment Setup
- [ ] Set up production PostgreSQL database
- [ ] Configure production Redis instance
- [ ] Set up monitoring and logging
- [ ] Implement health check endpoints
- [ ] Configure production environment variables

### Phase 9.2: Deployment Configuration
- [ ] Create Docker containers for all services
- [ ] Set up Docker Compose for local development
- [ ] Configure CI/CD pipeline
- [ ] Implement automated testing
- [ ] Set up staging environment

### Phase 9.3: Hosting & Domain Setup
- [ ] Deploy to Fly.io or Render
- [ ] Configure custom domain and SSL
- [ ] Set up CDN for static assets
- [ ] Implement backup strategies
- [ ] Configure monitoring and alerting

### Phase 9.4: Documentation & Launch
- [ ] Create comprehensive API documentation
- [ ] Write user guide and tutorials
- [ ] Create deployment documentation
- [ ] Set up support channels
- [ ] Plan public launch strategy

---

## Success Metrics & KPIs

### Technical Metrics
- **Performance**: API response time < 200ms for dashboard
- **Reliability**: 99.9% uptime for core services
- **Scalability**: Support 100+ projects per user
- **Security**: Zero critical security vulnerabilities

### User Experience Metrics
- **Onboarding**: < 2 minutes to add first project
- **Accuracy**: 95%+ accuracy in plan parsing
- **Automation**: 90%+ of updates via webhooks
- **Engagement**: Daily active usage for 70%+ of users

### Business Metrics
- **Adoption**: 100+ active users within 3 months
- **Retention**: 80%+ monthly user retention
- **Growth**: 20%+ month-over-month user growth
- **Feedback**: 4.5+ star rating on GitHub

---

## Risk Mitigation

### Technical Risks
- **GitHub API rate limits**: Implement caching and rate limit handling
- **Repository access issues**: Add comprehensive error handling and fallbacks
- **Parsing accuracy**: Extensive testing with diverse plan formats
- **Performance degradation**: Regular performance monitoring and optimization

### Operational Risks
- **Data loss**: Implement automated backups and recovery procedures
- **Service downtime**: Set up monitoring and alerting systems
- **Security vulnerabilities**: Regular security audits and updates
- **Scalability issues**: Design for horizontal scaling from the start

---

## Future Enhancements (Post-v1.0)

### Advanced Integrations
- GitLab and Bitbucket support
- Jira and Linear integration
- Slack/Discord notifications
- Email reporting and summaries

### AI/ML Features
- LLM-generated project summaries
- Intelligent task categorization
- Predictive progress modeling
- Automated skill recommendations

### Enterprise Features
- Multi-user support with roles
- Organization-wide analytics
- Advanced reporting and exports
- Custom integrations and webhooks

---

**Total Estimated Timeline**: 18 weeks (4.5 months)
**Team Size**: 1-2 developers
**Technology Stack**: FastAPI + Next.js + PostgreSQL + Redis
**Deployment Target**: Fly.io/Render with custom domain
