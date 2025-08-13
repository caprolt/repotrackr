import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, DECIMAL, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    repo_url = Column(String(500), nullable=False, unique=True)
    plan_path = Column(String(255), default="docs/plan.md")
    status = Column(Enum("green", "yellow", "red", "processing", "failed", name="project_status"), default="yellow")
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    progress_snapshots = relationship("ProgressSnapshot", back_populates="project", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="project", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_projects_status", "status"),
        Index("idx_projects_last_updated", "last_updated"),
    )


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    status = Column(Enum("todo", "doing", "done", "blocked", name="task_status"), default="todo")
    file_path = Column(String(500))
    line_number = Column(Integer)
    commit_hash = Column(String(40))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    
    # Indexes
    __table_args__ = (
        Index("idx_tasks_project_id", "project_id"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_file_path", "file_path"),
    )


class ProgressSnapshot(Base):
    __tablename__ = "progress_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    percentage_complete = Column(DECIMAL(5, 2))
    tasks_total = Column(Integer, default=0)
    tasks_done = Column(Integer, default=0)
    tasks_doing = Column(Integer, default=0)
    tasks_todo = Column(Integer, default=0)
    tasks_blocked = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="progress_snapshots")
    
    # Indexes
    __table_args__ = (
        Index("idx_snapshots_project_id", "project_id"),
        Index("idx_snapshots_created_at", "created_at"),
    )


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # e.g., 'language', 'framework', 'tool'
    source = Column(String(255))  # e.g., 'requirements.txt', 'package.json'
    confidence = Column(DECIMAL(3, 2))  # 0-1 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="skills")
    
    # Indexes
    __table_args__ = (
        Index("idx_skills_project_id", "project_id"),
        Index("idx_skills_category", "category"),
        Index("idx_skills_name", "name"),
    )
