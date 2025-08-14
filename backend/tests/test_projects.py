import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_project():
    """Test creating a new project."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project",
                "repo_url": "https://github.com/testuser/create-test-project",
                "plan_path": "docs/plan.md"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["repo_url"] == "https://github.com/testuser/create-test-project"
    assert data["plan_path"] == "docs/plan.md"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_project_duplicate_repo():
    """Test creating a project with duplicate repo URL."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create first project
        response1 = await ac.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project 1",
                "repo_url": "https://github.com/testuser/duplicate",
                "plan_path": "docs/plan.md"
            }
        )
        assert response1.status_code == 200
        
        # Try to create second project with same repo URL
        response2 = await ac.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project 2",
                "repo_url": "https://github.com/testuser/duplicate",
                "plan_path": "docs/plan.md"
            }
        )
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_list_projects():
    """Test listing projects."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/projects/")
    
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


@pytest.mark.asyncio
async def test_get_project():
    """Test getting a specific project."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First create a project
        create_response = await ac.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project",
                "repo_url": "https://github.com/testuser/get-test-project",
                "plan_path": "docs/plan.md"
            }
        )
        project_id = create_response.json()["id"]
        
        # Then get the project
        response = await ac.get(f"/api/v1/projects/{project_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Test Project"


@pytest.mark.asyncio
async def test_get_project_not_found():
    """Test getting a non-existent project."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/projects/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_project():
    """Test deleting a project."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First create a project
        create_response = await ac.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project",
                "repo_url": "https://github.com/testuser/delete-test-project",
                "plan_path": "docs/plan.md"
            }
        )
        project_id = create_response.json()["id"]
        
        # Then delete the project
        response = await ac.delete(f"/api/v1/projects/{project_id}")
    
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


@pytest.mark.asyncio
async def test_update_project():
    """Test updating a project."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First create a project
        create_response = await ac.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project",
                "repo_url": "https://github.com/testuser/update-test-project-unique",
                "plan_path": "docs/plan.md"
            }
        )
        project_id = create_response.json()["id"]
        
        # Then update the project
        response = await ac.put(
            f"/api/v1/projects/{project_id}",
            json={
                "name": "Updated Test Project",
                "plan_path": "docs/updated-plan.md"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Updated Test Project"
    assert data["plan_path"] == "docs/updated-plan.md"
    assert data["repo_url"] == "https://github.com/testuser/update-test-project-unique"  # Should remain unchanged


@pytest.mark.asyncio
async def test_update_project_not_found():
    """Test updating a non-existent project."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            "/api/v1/projects/00000000-0000-0000-0000-000000000000",
            json={
                "name": "Updated Test Project"
            }
        )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_project_duplicate_repo():
    """Test updating a project with duplicate repo URL."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create first project
        response1 = await ac.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project 1",
                "repo_url": "https://github.com/testuser/project1",
                "plan_path": "docs/plan.md"
            }
        )
        project1_id = response1.json()["id"]
        
        # Create second project
        response2 = await ac.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project 2",
                "repo_url": "https://github.com/testuser/project2",
                "plan_path": "docs/plan.md"
            }
        )
        project2_id = response2.json()["id"]
        
        # Try to update second project with first project's repo URL
        response3 = await ac.put(
            f"/api/v1/projects/{project2_id}",
            json={
                "repo_url": "https://github.com/testuser/project1"
            }
        )
    
    assert response3.status_code == 400
    assert "already exists" in response3.json()["detail"]
