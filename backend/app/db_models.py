from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True)
    login = Column(String)
    email = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    access_token = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    runs = relationship("AgentRun", back_populates="user")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    repo = Column(String)
    repo_name = Column(String)
    branch = Column(String)
    team = Column(String, nullable=True)
    leader = Column(String, nullable=True)
    status = Column(String)  # PASSED, PARTIAL, FAILED
    total_failures = Column(Integer, default=0)
    total_fixes = Column(Integer, default=0)
    iterations = Column(Integer, default=0)
    fixes = Column(JSON)  # List of fix details
    duration = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="runs")
