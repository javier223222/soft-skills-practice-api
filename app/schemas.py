from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models import SoftSkillCategory, PracticeStatus


# Request models
class PracticeStartRequest(BaseModel):
    user_id: str
    soft_skill_id: int
    scenario_id: int
    

class PracticeSubmitRequest(BaseModel):
    session_id: str
    user_input: str
    duration_seconds: int


class CustomScenarioRequest(BaseModel):
    user_id: str
    soft_skill_id: int
    custom_scenario: str


# Response models
class SoftSkillResponse(BaseModel):
    id: int
    name: str
    description: str
    category: SoftSkillCategory
    icon_name: str
    color_theme: str
    progress_percentage: Optional[float] = None
    total_points: Optional[int] = None


class ScenarioResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty_level: int
    estimated_duration_minutes: int
    is_popular: bool


class PracticeSessionResponse(BaseModel):
    session_id: str
    user_id: str
    soft_skill: SoftSkillResponse
    scenario: ScenarioResponse
    status: PracticeStatus
    started_at: datetime


class ScoreBreakdown(BaseModel):
    clarity_score: Optional[int] = None
    empathy_score: Optional[int] = None
    assertiveness_score: Optional[int] = None
    listening_score: Optional[int] = None
    confidence_score: Optional[int] = None
    overall_score: Optional[float] = None


class FeedbackResponse(BaseModel):
    overall_feedback: str
    clarity_feedback: Optional[str] = None
    empathy_feedback: Optional[str] = None
    assertiveness_feedback: Optional[str] = None
    listening_feedback: Optional[str] = None
    confidence_feedback: Optional[str] = None
    improvement_areas: List[str] = []


class PracticeResultResponse(BaseModel):
    session_id: str
    status: PracticeStatus
    scores: ScoreBreakdown
    feedback: FeedbackResponse
    points_earned: int
    duration_seconds: int
    completed_at: datetime


class ProgressMetrics(BaseModel):
    total_practices: int
    completed_practices: int
    average_score: Optional[float] = None
    progress_percentage: float
    total_points: int
    best_scores: ScoreBreakdown


class SoftSkillProgressResponse(BaseModel):
    soft_skill: SoftSkillResponse
    metrics: ProgressMetrics
    first_practice_at: Optional[datetime] = None
    last_practice_at: Optional[datetime] = None


class UserProgressSummary(BaseModel):
    user_id: str
    total_points: int
    total_completed_practices: int
    soft_skills_progress: List[SoftSkillProgressResponse]
    improvement_areas: List[str] = []


# Event models (for EventBus integration)
class PracticeEvent(BaseModel):
    event_type: str
    user_id: str
    session_id: str
    soft_skill_id: int
    scenario_id: int
    timestamp: datetime
    metadata: dict = {}


class ProgressUpdateEvent(BaseModel):
    event_type: str = "progress_updated"
    user_id: str
    soft_skill_id: int
    previous_progress: float
    new_progress: float
    points_earned: int
    timestamp: datetime


# Error responses
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None


# Health check response
class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime
