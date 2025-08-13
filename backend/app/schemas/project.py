from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, validator
import uuid


class ProjectBase(BaseModel):
    name: str
    repo_url: str
    plan_path: Optional[str] = "docs/plan.md"
    
    @validator('repo_url')
    def validate_repo_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('repo_url must be a valid HTTP/HTTPS URL')
        return v


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    repo_url: Optional[str] = None
    plan_path: Optional[str] = None
    
    @validator('repo_url')
    def validate_repo_url(cls, v):
        if v is not None and not v.startswith(('http://', 'https://')):
            raise ValueError('repo_url must be a valid HTTP/HTTPS URL')
        return v


class ProjectInDB(ProjectBase):
    id: uuid.UUID
    status: str
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectResponse(ProjectInDB):
    pass


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    limit: int
    offset: int
