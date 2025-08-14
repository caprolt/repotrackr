from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel
import uuid


class SkillBase(BaseModel):
    name: str
    category: str
    confidence: float
    source: str


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    confidence: Optional[float] = None
    source: Optional[str] = None


class SkillInDB(SkillBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class SkillResponse(SkillInDB):
    pass


class SkillsResponse(BaseModel):
    skills: List[SkillResponse]
    total: int
    categories: Dict[str, int]


class SkillCategoryResponse(BaseModel):
    category: str
    skills: List[SkillResponse]
    count: int


class PopularSkillResponse(BaseModel):
    name: str
    category: str
    count: int


class SkillsOverviewResponse(BaseModel):
    total_skills: int
    categories: Dict[str, int]
    popular_skills: List[PopularSkillResponse]
