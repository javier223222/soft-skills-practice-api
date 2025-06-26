from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class SoftSkillCategory(str, Enum):
    COMMUNICATION = "communication"
    LEADERSHIP = "leadership"
    PROBLEM_SOLVING = "problem_solving"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    TEAMWORK = "teamwork"


class PracticeStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SoftSkill(SQLModel, table=True):
    __tablename__ = "soft_skills"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: str = Field(max_length=500)
    category: SoftSkillCategory
    icon_name: str = Field(max_length=50)  # For UI display
    color_theme: str = Field(max_length=20)  # For UI display
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    scenarios: List["SoftSkillScenario"] = Relationship(back_populates="soft_skill")
    practices: List["PracticeTracking"] = Relationship(back_populates="soft_skill")
    progress: List["SoftSkillProgress"] = Relationship(back_populates="soft_skill")


class SoftSkillScenario(SQLModel, table=True):
    __tablename__ = "soft_skill_scenarios"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    soft_skill_id: int = Field(foreign_key="soft_skills.id")
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    difficulty_level: int = Field(ge=1, le=5)  # 1=Easy, 5=Expert
    estimated_duration_minutes: int = Field(ge=1, le=60)
    is_popular: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    soft_skill: SoftSkill = Relationship(back_populates="scenarios")
    practices: List["PracticeTracking"] = Relationship(back_populates="scenario")


class PracticeTracking(SQLModel, table=True):
    __tablename__ = "practice_tracking"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True)
    user_id: str = Field(max_length=100)  # External user ID
    soft_skill_id: int = Field(foreign_key="soft_skills.id")
    scenario_id: int = Field(foreign_key="soft_skill_scenarios.id")
    
    # Practice details
    status: PracticeStatus = Field(default=PracticeStatus.STARTED)
    user_input: Optional[str] = Field(default=None)  # User's response/approach
    duration_seconds: Optional[int] = Field(default=None)
    
    # Scoring (based on UI metrics)
    clarity_score: Optional[int] = Field(default=None, ge=1, le=5)
    empathy_score: Optional[int] = Field(default=None, ge=1, le=5)
    assertiveness_score: Optional[int] = Field(default=None, ge=1, le=5)
    listening_score: Optional[int] = Field(default=None, ge=1, le=5)
    confidence_score: Optional[int] = Field(default=None, ge=1, le=5)
    overall_score: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    
    # Points earned
    points_earned: int = Field(default=0)
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    soft_skill: SoftSkill = Relationship(back_populates="practices")
    scenario: SoftSkillScenario = Relationship(back_populates="practices")
    feedback: Optional["FeedbackPractice"] = Relationship(back_populates="practice")


class FeedbackPractice(SQLModel, table=True):
    __tablename__ = "feedback_practice"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    practice_id: int = Field(foreign_key="practice_tracking.id", unique=True)
    
    # Feedback content
    overall_feedback: str = Field(max_length=2000)
    clarity_feedback: Optional[str] = Field(default=None, max_length=500)
    empathy_feedback: Optional[str] = Field(default=None, max_length=500)
    assertiveness_feedback: Optional[str] = Field(default=None, max_length=500)
    listening_feedback: Optional[str] = Field(default=None, max_length=500)
    confidence_feedback: Optional[str] = Field(default=None, max_length=500)
    
    # Improvement areas (tags)
    improvement_areas: Optional[str] = Field(default="[]", description="JSON array of improvement areas")
    
    # LLM metadata
    llm_model_used: str = Field(max_length=100)
    llm_response_time_ms: Optional[int] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    practice: PracticeTracking = Relationship(back_populates="feedback")


class SoftSkillProgress(SQLModel, table=True):
    __tablename__ = "soft_skill_progress"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=100)
    soft_skill_id: int = Field(foreign_key="soft_skills.id")
    
    # Progress metrics
    total_practices: int = Field(default=0, ge=0)
    completed_practices: int = Field(default=0, ge=0)
    average_score: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    total_points: int = Field(default=0, ge=0)
    
    # Best scores
    best_clarity_score: Optional[int] = Field(default=None, ge=1, le=5)
    best_empathy_score: Optional[int] = Field(default=None, ge=1, le=5)
    best_assertiveness_score: Optional[int] = Field(default=None, ge=1, le=5)
    best_listening_score: Optional[int] = Field(default=None, ge=1, le=5)
    best_confidence_score: Optional[int] = Field(default=None, ge=1, le=5)
    
    # Timestamps
    first_practice_at: Optional[datetime] = Field(default=None)
    last_practice_at: Optional[datetime] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    soft_skill: SoftSkill = Relationship(back_populates="progress")
    
    class Config:
        # Ensure unique combination of user and soft skill
        indexes = [("user_id", "soft_skill_id")]


class TrackingLog(SQLModel, table=True):
    __tablename__ = "tracking_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=100)
    practice_session_id: Optional[str] = Field(default=None)
    event_type: str = Field(max_length=50)  # "practice_started", "practice_completed", etc.
    event_data: Optional[str] = Field(default="{}", description="JSON string for event data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # For analytics and auditing
    user_agent: Optional[str] = Field(default=None, max_length=500)
    ip_address: Optional[str] = Field(default=None, max_length=45)
