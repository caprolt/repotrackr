# Phase 4: Skills Extraction System (Weeks 7-8)

## Overview
This phase implements the skills extraction system that analyzes project dependency files to identify and categorize the technologies, frameworks, and tools used in each project.

## Dependencies
- Phase 1: Foundation & Core Infrastructure
- Phase 2: Plan Parsing Engine
- Phase 3: Frontend Foundation
- Database schema must include skills table
- Repository cloning must be functional

## Deliverables
- Manifest file parsing system
- Skill categorization engine
- Skills display integration
- Confidence scoring system
- Skills database with mappings

---

## Phase 4.1: Manifest File Parsing

### Tasks
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

### Technical Details
- **File Discovery**: Recursive search for manifest files
- **Parser Libraries**: Use appropriate libraries for each format
- **Version Handling**: Extract and normalize version information
- **Comment Handling**: Skip comments and empty lines
- **Error Recovery**: Graceful handling of malformed files

### Parser Implementation
```python
class ManifestParser:
    async def parse_requirements_txt(self, content: str) -> List[Package]
    async def parse_package_json(self, content: str) -> List[Package]
    async def parse_dockerfile(self, content: str) -> List[Package]
    async def parse_pyproject_toml(self, content: str) -> List[Package]
    async def parse_cargo_toml(self, content: str) -> List[Package]
    async def parse_go_mod(self, content: str) -> List[Package]

class Package:
    name: str
    version: Optional[str]
    source: str  # filename
    category: Optional[str]
    confidence: float
```

### Supported File Formats

#### requirements.txt
```txt
# Web framework
Django==4.2.0
Flask>=2.3.0

# Database
psycopg2-binary
redis

# Testing
pytest>=7.0.0
```

#### package.json
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "next": "14.0.0",
    "@types/node": "^20.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "tailwindcss": "^3.0.0"
  },
  "scripts": {
    "build": "next build",
    "test": "jest"
  }
}
```

#### Dockerfile
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y git
COPY requirements.txt .
RUN pip install -r requirements.txt
```

### Acceptance Criteria
- [ ] All manifest file types parsed correctly
- [ ] Package names and versions extracted
- [ ] Comments and empty lines handled
- [ ] Error handling for malformed files
- [ ] Support for version specifiers

---

## Phase 4.2: Skill Categorization Engine

### Tasks
- [ ] Create skill mapping database:
  - Language detection (Python, JavaScript, Rust, Go)
  - Framework categorization (React, Django, FastAPI)
  - Tool classification (Docker, Git, CI/CD)
- [ ] Implement confidence scoring algorithm
- [ ] Add skill normalization (case-insensitive matching)
- [ ] Create skill deduplication logic
- [ ] Add custom skill category support

### Technical Details
- **Skill Database**: Comprehensive mapping of packages to skills
- **Confidence Scoring**: Algorithm based on package popularity and usage
- **Normalization**: Case-insensitive matching and aliases
- **Deduplication**: Remove duplicate skills across files
- **Custom Categories**: User-defined skill categories

### Skill Mapping Database
```python
class SkillMapper:
    async def map_package_to_skill(self, package: Package) -> Skill
    async def get_skill_confidence(self, package: Package) -> float
    async def normalize_skill_name(self, name: str) -> str
    async def deduplicate_skills(self, skills: List[Skill]) -> List[Skill]

class Skill:
    name: str
    category: str  # language, framework, tool, database, etc.
    confidence: float
    source: str
    aliases: List[str]
```

### Skill Categories
- **Languages**: Python, JavaScript, TypeScript, Rust, Go, Java, C#, etc.
- **Frameworks**: React, Vue, Angular, Django, Flask, FastAPI, Express, etc.
- **Tools**: Docker, Git, npm, pip, cargo, go mod, etc.
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis, etc.
- **Cloud**: AWS, Azure, GCP, Heroku, etc.
- **Testing**: pytest, jest, mocha, cypress, etc.
- **Build Tools**: webpack, vite, rollup, etc.

### Confidence Scoring Algorithm
```python
def calculate_confidence(package: Package) -> float:
    base_confidence = 0.5
    
    # Popularity boost
    if package.name in POPULAR_PACKAGES:
        base_confidence += 0.3
    
    # Version specificity
    if package.version:
        base_confidence += 0.1
    
    # Source file reliability
    if package.source in RELIABLE_SOURCES:
        base_confidence += 0.1
    
    return min(base_confidence, 1.0)
```

### Acceptance Criteria
- [ ] Skill mapping database comprehensive
- [ ] Confidence scoring algorithm working
- [ ] Skill normalization functional
- [ ] Deduplication logic working
- [ ] Custom categories supported

---

## Phase 4.3: Skills Display Integration

### Tasks
- [ ] Update project detail page with skills section
- [ ] Create skill chip components with categories
- [ ] Implement skill filtering and sorting
- [ ] Add skill confidence indicators
- [ ] Create skills overview on dashboard

### Technical Details
- **Skill Chips**: Visual representation of skills
- **Category Grouping**: Group skills by category
- **Confidence Indicators**: Visual indicators for confidence levels
- **Filtering**: Filter skills by category or confidence
- **Dashboard Integration**: Skills overview on main dashboard

### Frontend Components
```typescript
// SkillChip component
interface SkillChipProps {
  skill: Skill;
  showConfidence?: boolean;
  onClick?: () => void;
}

// SkillsSection component
interface SkillsSectionProps {
  skills: Skill[];
  projectId: string;
}

// SkillsOverview component
interface SkillsOverviewProps {
  projects: Project[];
}
```

### Skills Display Features
- **Category Tabs**: Tabbed interface by skill category
- **Confidence Indicators**: Color-coded confidence levels
- **Skill Counts**: Display skill counts per category
- **Search/Filter**: Filter skills by name or category
- **Tooltips**: Show additional skill information
- **Responsive Design**: Mobile-friendly skill display

### Skills Dashboard Overview
- **Most Used Skills**: Top skills across all projects
- **Skill Distribution**: Chart showing skill categories
- **Recent Skills**: Recently added skills
- **Skill Trends**: Skills usage over time

### Acceptance Criteria
- [ ] Skills section added to project detail page
- [ ] Skill chips display correctly
- [ ] Category grouping functional
- [ ] Confidence indicators working
- [ ] Dashboard skills overview complete
- [ ] Filtering and sorting working

---

## API Endpoints

### New Endpoints
- `GET /projects/{id}/skills` - Get project skills
- `GET /skills/categories` - Get skill categories
- `GET /skills/popular` - Get popular skills
- `POST /projects/{id}/extract-skills` - Trigger skills extraction

### Skills Response Format
```json
{
  "skills": [
    {
      "name": "Python",
      "category": "language",
      "confidence": 0.95,
      "source": "requirements.txt",
      "aliases": ["python", "py"]
    },
    {
      "name": "React",
      "category": "framework",
      "confidence": 0.88,
      "source": "package.json",
      "aliases": ["react", "reactjs"]
    }
  ],
  "categories": {
    "language": 2,
    "framework": 3,
    "tool": 1
  }
}
```

---

## Integration with Processing Pipeline

### Skills Extraction Integration
```python
class SkillsExtractionPipeline:
    async def extract_skills_from_project(self, project_id: str) -> List[Skill]
    async def process_manifest_files(self, repo_path: str) -> List[Package]
    async def store_skills(self, project_id: str, skills: List[Skill])
    async def update_project_skills(self, project_id: str)
```

### Processing Steps
1. Clone repository (reuse from Phase 2)
2. Discover manifest files
3. Parse each manifest file
4. Map packages to skills
5. Calculate confidence scores
6. Deduplicate skills
7. Store in database

---

## Testing Strategy

### Unit Tests
- Manifest file parser tests
- Skill mapping tests
- Confidence scoring tests
- Deduplication tests

### Integration Tests
- End-to-end skills extraction
- Database integration tests
- Frontend integration tests

### Manual Testing
- Test with various project types
- Test with different manifest formats
- Test skill categorization accuracy

---

## Definition of Done
- [ ] All tasks completed and tested
- [ ] Manifest file parsing functional
- [ ] Skill categorization working
- [ ] Skills display integrated
- [ ] Confidence scoring accurate
- [ ] Frontend integration complete
- [ ] Ready for Phase 5 development

---

## Next Phase Dependencies
- Skills extraction must be functional
- Skills display must be integrated
- Processing pipeline must include skills
- Frontend must display skills correctly
