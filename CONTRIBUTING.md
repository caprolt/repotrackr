# Contributing to RepoTrackr

First off, thank you for considering contributing to RepoTrackr! It's people like you that make RepoTrackr such a great tool.

## Code of Conduct

This project and everyone participating in it is expected to maintain a welcoming and inclusive environment. Be respectful, professional, and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python/Node versions, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a **clear and descriptive title**
- Provide a **detailed description** of the proposed feature
- Explain **why this enhancement would be useful**
- Include **mockups or examples** if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow the coding standards** outlined below
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Ensure all tests pass** before submitting
6. **Write clear commit messages**

## Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- Git

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/repotrackr.git
cd repotrackr

# Start infrastructure
docker-compose up -d

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head

# Frontend setup
cd ../frontend
npm install
cp .env.example .env.local
```

## Coding Standards

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Write **docstrings** for classes and functions
- Use **async/await** for database operations
- Keep functions **small and focused**

```python
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

async def get_projects(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Project]:
    """
    Retrieve a list of projects from the database.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Project objects
    """
    # Implementation here
    pass
```

### TypeScript (Frontend)

- Follow **TypeScript best practices**
- Use **functional components** with hooks
- Define **interfaces** for all props and data structures
- Use **meaningful variable names**
- Keep components **small and reusable**

```typescript
interface ProjectCardProps {
  project: Project;
  onRefresh: (id: string) => Promise<void>;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ 
  project, 
  onRefresh 
}) => {
  // Component implementation
};
```

### Code Formatting

**Backend:**
```bash
# Format code
black .

# Lint
flake8

# Type checking
mypy app/
```

**Frontend:**
```bash
# Format code
npm run format

# Lint
npm run lint

# Type check
npm run type-check
```

## Testing

### Writing Tests

**Backend (pytest):**
```python
# tests/test_projects.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    response = await client.post(
        "/api/v1/projects/",
        json={
            "name": "Test Project",
            "repository_url": "https://github.com/user/repo"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
```

**Frontend (Jest/React Testing Library):**
```typescript
// components/__tests__/ProjectCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ProjectCard } from '../ProjectCard';

test('renders project name', () => {
  const project = { name: 'Test Project', /* ... */ };
  render(<ProjectCard project={project} />);
  expect(screen.getByText('Test Project')).toBeInTheDocument();
});
```

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Database Migrations

When making database schema changes:

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Add new column to projects"

# Review the generated migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat: add GitHub webhook integration
fix: resolve task parsing for nested lists
docs: update installation instructions
refactor: simplify progress calculation logic
test: add tests for skill extraction
```

### Pull Request Process

1. Update your branch with the latest `main`:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. Push your changes:
   ```bash
   git push origin your-branch
   ```

3. Create a pull request with:
   - Clear title following commit message conventions
   - Description of changes
   - Link to related issues
   - Screenshots if applicable
   - Checklist of completed items

4. Address review feedback and update PR

5. Once approved, a maintainer will merge your PR

## Project Structure

```
repotrackr/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Config and settings
│   │   ├── db/              # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── alembic/             # Migrations
│   ├── tests/               # Tests
│   └── scripts/             # Utility scripts
├── frontend/
│   ├── app/                 # Next.js pages
│   ├── components/          # React components
│   ├── lib/                 # Utilities
│   └── __tests__/          # Tests
├── docs/                    # Documentation
└── scripts/                 # Development scripts
```

## Architecture Decisions

### Backend

- **FastAPI** for modern async Python web framework
- **SQLAlchemy 2.0** with async support
- **PostgreSQL** for relational data with JSONB support
- **Alembic** for database migrations
- **Pydantic** for data validation and serialization

### Frontend

- **Next.js 14** with App Router for React framework
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Lucide React** for icons

### Infrastructure

- **Docker Compose** for local development
- **PostgreSQL** for database
- **Redis** for job queue (future feature)

## Questions?

Feel free to:
- Open an issue for questions
- Reach out to [@caprolt](https://github.com/caprolt)
- Check existing documentation in `/docs`

Thank you for contributing! 🎉
