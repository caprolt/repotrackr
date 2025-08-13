# Phase 6: GitHub Integration & Webhooks (Weeks 11-12)

## Overview
This phase implements GitHub integration with webhooks to enable real-time updates when repositories change, providing automatic project tracking without manual intervention.

## Dependencies
- Phase 1: Foundation & Core Infrastructure
- Phase 2: Plan Parsing Engine
- Phase 3: Frontend Foundation
- Phase 4: Skills Extraction System
- Phase 5: Background Processing & Automation
- Background job processing must be functional
- GitHub App must be created and configured

## Deliverables
- GitHub App with proper permissions
- Webhook endpoint with signature verification
- Real-time event processing
- Automatic project updates
- Webhook health monitoring

---

## Phase 6.1: GitHub App Setup

### Tasks
- [ ] Create GitHub App with required permissions:
  - `contents:read` for file access
  - `metadata:read` for repository info
- [ ] Configure webhook endpoints
- [ ] Implement app installation flow
- [ ] Add repository access validation

### Technical Details
- **GitHub App**: Create app in GitHub Developer Settings
- **Permissions**: Minimal required permissions for security
- **Webhook URL**: Configure webhook endpoint URL
- **Installation Flow**: Handle app installation process
- **Access Validation**: Verify repository access permissions

### GitHub App Configuration
```yaml
# GitHub App settings
name: "RepoTrackr"
description: "Automated project tracking system"
homepage_url: "https://repotrackr.com"
callback_url: "https://repotrackr.com/auth/github/callback"
webhook_url: "https://repotrackr.com/webhooks/github"
webhook_secret: "your-webhook-secret"

# Permissions
permissions:
  contents: "read"
  metadata: "read"

# Events to subscribe to
default_events:
  - push
  - pull_request
  - issues
```

### GitHub App Installation
```python
class GitHubAppManager:
    async def create_installation_token(self, installation_id: int) -> str
    async def get_installation_repositories(self, installation_id: int) -> List[dict]
    async def validate_repository_access(self, repo_url: str, installation_id: int) -> bool
    async def handle_installation_created(self, installation_data: dict)
    async def handle_installation_deleted(self, installation_id: int)

# Installation flow
@router.post("/auth/github/install")
async def github_install_callback(
    code: str,
    state: str,
    current_user: User = Depends(get_current_user)
) -> dict:
    """Handle GitHub App installation callback"""
    
    # Exchange code for installation token
    installation_data = await exchange_installation_code(code)
    
    # Store installation info
    await store_installation(installation_data, current_user.id)
    
    return {
        "status": "success",
        "installation_id": installation_data["id"]
    }
```

### Repository Access Validation
```python
async def validate_repository_access(repo_url: str, user_id: str) -> bool:
    """Validate that user has access to repository"""
    
    # Get user's GitHub installations
    installations = await get_user_installations(user_id)
    
    for installation in installations:
        # Check if repository is accessible
        if await check_repo_access(repo_url, installation.id):
            return True
    
    return False
```

### Acceptance Criteria
- [ ] GitHub App created successfully
- [ ] Permissions configured correctly
- [ ] Webhook URL configured
- [ ] Installation flow working
- [ ] Repository access validation functional

---

## Phase 6.2: Webhook Implementation

### Tasks
- [ ] Create `/webhooks/github` endpoint
- [ ] Implement webhook signature verification
- [ ] Handle relevant GitHub events:
  - `push` events for plan file changes
  - `pull_request` events for review tracking
  - `issues` events for issue-based planning
- [ ] Add webhook event filtering and processing
- [ ] Implement webhook retry logic

### Technical Details
- **Signature Verification**: Verify webhook signatures for security
- **Event Filtering**: Process only relevant events
- **Event Processing**: Handle different event types appropriately
- **Retry Logic**: Implement retry for failed webhook processing
- **Logging**: Comprehensive webhook event logging

### Webhook Endpoint
```python
@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_github_delivery: str = Header(None),
    x_hub_signature_256: str = Header(None)
) -> dict:
    """Handle GitHub webhook events"""
    
    # Get webhook payload
    payload = await request.json()
    
    # Verify webhook signature
    if not verify_webhook_signature(request, x_hub_signature_256):
        raise HTTPException(401, "Invalid webhook signature")
    
    # Process webhook event
    try:
        await process_github_event(x_github_event, payload, x_github_delivery)
        return {"status": "processed"}
    except Exception as e:
        # Log error and return 200 to prevent GitHub retries
        logger.error(f"Webhook processing failed: {e}")
        return {"status": "error", "message": str(e)}
```

### Webhook Signature Verification
```python
import hmac
import hashlib

def verify_webhook_signature(request: Request, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    
    if not signature:
        return False
    
    # Get webhook secret
    webhook_secret = settings.GITHUB_WEBHOOK_SECRET
    
    # Get request body
    body = request.body()
    
    # Calculate expected signature
    expected_signature = "sha256=" + hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

### Event Processing
```python
class GitHubEventProcessor:
    async def process_push_event(self, payload: dict) -> None
    async def process_pull_request_event(self, payload: dict) -> None
    async def process_issues_event(self, payload: dict) -> None
    
    async def process_github_event(self, event_type: str, payload: dict, delivery_id: str) -> None:
        """Process GitHub webhook event"""
        
        # Log event
        await log_webhook_event(event_type, payload, delivery_id)
        
        # Route to appropriate handler
        if event_type == "push":
            await self.process_push_event(payload)
        elif event_type == "pull_request":
            await self.process_pull_request_event(payload)
        elif event_type == "issues":
            await self.process_issues_event(payload)
        else:
            logger.info(f"Ignoring event type: {event_type}")

async def process_push_event(payload: dict) -> None:
    """Process push event"""
    
    repository = payload["repository"]
    commits = payload["commits"]
    
    # Find projects using this repository
    projects = await find_projects_by_repo(repository["full_name"])
    
    for project in projects:
        # Check if plan file or manifest files were changed
        if files_changed_in_commits(commits, project.plan_path) or \
           files_changed_in_commits(commits, MANIFEST_FILES):
            
            # Trigger background processing
            await enqueue_project_processing(project.id, priority="high")
```

### Event Filtering
```python
def files_changed_in_commits(commits: List[dict], target_files: List[str]) -> bool:
    """Check if any target files were changed in commits"""
    
    for commit in commits:
        for file_path in commit.get("added", []) + commit.get("modified", []):
            if any(file_path.endswith(target) for target in target_files):
                return True
    
    return False

# Files to monitor for changes
PLAN_FILES = ["docs/plan.md", "plan.md", "README.md"]
MANIFEST_FILES = [
    "requirements.txt", "package.json", "Dockerfile",
    "pyproject.toml", "Cargo.toml", "go.mod"
]
```

### Acceptance Criteria
- [ ] Webhook endpoint functional
- [ ] Signature verification working
- [ ] Event processing implemented
- [ ] Event filtering working
- [ ] Retry logic functional

---

## Phase 6.3: Real-time Updates

### Tasks
- [ ] Trigger background jobs on webhook events
- [ ] Update project status automatically
- [ ] Create new progress snapshots
- [ ] Add webhook event logging
- [ ] Implement webhook health monitoring

### Technical Details
- **Background Job Triggering**: Enqueue processing jobs on webhook events
- **Automatic Updates**: Update project status without user intervention
- **Snapshot Creation**: Create new progress snapshots for tracking
- **Event Logging**: Log all webhook events for debugging
- **Health Monitoring**: Monitor webhook endpoint health

### Real-time Update Pipeline
```python
class RealTimeUpdatePipeline:
    async def handle_repository_update(self, repo_name: str, event_type: str) -> None:
        """Handle repository update from webhook"""
        
        # Find affected projects
        projects = await find_projects_by_repo(repo_name)
        
        for project in projects:
            # Enqueue processing job
            job_id = await enqueue_project_processing(project.id, priority="high")
            
            # Log update event
            await log_project_update(project.id, event_type, job_id)
            
            # Update project last_updated timestamp
            await update_project_timestamp(project.id)

async def log_project_update(project_id: str, event_type: str, job_id: str) -> None:
    """Log project update event"""
    
    await db.execute(
        """
        INSERT INTO project_updates (project_id, event_type, job_id, created_at)
        VALUES (:project_id, :event_type, :job_id, NOW())
        """,
        {"project_id": project_id, "event_type": event_type, "job_id": job_id}
    )
```

### Webhook Event Logging
```python
class WebhookEventLogger:
    async def log_event(self, event_type: str, payload: dict, delivery_id: str) -> None:
        """Log webhook event"""
        
        await db.execute(
            """
            INSERT INTO webhook_events (
                delivery_id, event_type, payload, processed_at, created_at
            ) VALUES (:delivery_id, :event_type, :payload, NOW(), NOW())
            """,
            {
                "delivery_id": delivery_id,
                "event_type": event_type,
                "payload": json.dumps(payload)
            }
        )

    async def get_event_stats(self, hours: int = 24) -> dict:
        """Get webhook event statistics"""
        
        result = await db.fetch_one(
            """
            SELECT 
                event_type,
                COUNT(*) as count,
                COUNT(CASE WHEN processed_at IS NOT NULL THEN 1 END) as processed
            FROM webhook_events
            WHERE created_at > NOW() - INTERVAL ':hours hours'
            GROUP BY event_type
            """,
            {"hours": hours}
        )
        
        return result
```

### Webhook Health Monitoring
```python
@router.get("/webhooks/github/health")
async def webhook_health_check() -> dict:
    """Check webhook endpoint health"""
    
    # Get recent webhook events
    recent_events = await get_recent_webhook_events(hours=1)
    
    # Calculate success rate
    total_events = len(recent_events)
    successful_events = len([e for e in recent_events if e.processed_at])
    success_rate = successful_events / total_events if total_events > 0 else 1.0
    
    # Check for recent failures
    recent_failures = await get_recent_webhook_failures(hours=1)
    
    return {
        "status": "healthy" if success_rate > 0.95 else "degraded",
        "success_rate": success_rate,
        "total_events_last_hour": total_events,
        "failed_events_last_hour": len(recent_failures),
        "last_event_at": recent_events[0].created_at if recent_events else None
    }
```

### Acceptance Criteria
- [ ] Background jobs triggered on webhook events
- [ ] Project status updated automatically
- [ ] Progress snapshots created
- [ ] Event logging implemented
- [ ] Health monitoring functional

---

## API Endpoints

### New Endpoints
- `POST /webhooks/github` - GitHub webhook endpoint
- `GET /webhooks/github/health` - Webhook health check
- `GET /webhooks/github/events` - Get webhook event history
- `POST /auth/github/install` - GitHub App installation callback
- `GET /auth/github/installations` - Get user's GitHub installations

### Webhook Event Response
```json
{
  "status": "processed",
  "event_type": "push",
  "delivery_id": "uuid",
  "processed_at": "2024-01-01T12:00:00Z"
}
```

---

## Security Considerations

### Webhook Security
- **Signature Verification**: Always verify webhook signatures
- **HTTPS Only**: Require HTTPS for webhook endpoints
- **Rate Limiting**: Implement rate limiting on webhook endpoints
- **Input Validation**: Validate all webhook payload data

### GitHub App Security
- **Minimal Permissions**: Request only necessary permissions
- **Token Management**: Properly manage installation tokens
- **Access Control**: Validate repository access before processing
- **Audit Logging**: Log all GitHub App interactions

---

## Testing Strategy

### Unit Tests
- Webhook signature verification tests
- Event processing tests
- GitHub App integration tests
- Security validation tests

### Integration Tests
- End-to-end webhook processing
- GitHub App installation flow
- Real-time update pipeline

### Manual Testing
- Test with actual GitHub repositories
- Test webhook event processing
- Test GitHub App installation

---

## Definition of Done
- [ ] All tasks completed and tested
- [ ] GitHub App configured and functional
- [ ] Webhook endpoint working correctly
- [ ] Real-time updates implemented
- [ ] Security measures in place
- [ ] Health monitoring functional
- [ ] Ready for Phase 7 development

---

## Next Phase Dependencies
- GitHub integration must be stable
- Webhook processing must be reliable
- Real-time updates must work correctly
- Security measures must be implemented
