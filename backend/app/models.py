from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))
    login = Column(String(50), unique=True)
    profile_picture = Column(String(255), default="/static/default_avatar.png")
    is_deleted = Column(Boolean, default=False)
    google_id = Column(String(100), unique=True)
    
    projects_owned = relationship("Project", back_populates="owner")
    tasks_assigned = relationship("Task", back_populates="assignee")
    project_memberships = relationship("ProjectMember", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    periodicity_id = Column(Integer, ForeignKey("sprint_periodicities.id"), nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="projects_owned")
    periodicity = relationship("SprintPeriodicity")
    members = relationship("ProjectMember", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    sprints = relationship("Sprint", back_populates="project")
    statuses = relationship("ProjectStatus", back_populates="project")

class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

class ProjectStatus(Base):
    __tablename__ = "project_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(50), nullable=False)
    order = Column(Integer, nullable=False)
    
    project = relationship("Project", back_populates="statuses")

class SprintPeriodicity(Base):
    __tablename__ = "sprint_periodicities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class Sprint(Base):
    __tablename__ = "sprints"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    planned_end_date = Column(DateTime, nullable=False)
    actual_end_date = Column(DateTime)
    
    project = relationship("Project", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    file_data = Column(LargeBinary)
    file_format = Column(String(10))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("project_statuses.id"))
    sprint_id = Column(Integer, ForeignKey("sprints.id"))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    assignee = relationship("User", back_populates="tasks_assigned")
    project = relationship("Project", back_populates="tasks")
    status = relationship("ProjectStatus")
    sprint = relationship("Sprint", back_populates="tasks")