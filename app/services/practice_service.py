from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import random

from app.models import (
    SoftSkill, SoftSkillScenario, PracticeTracking, 
    FeedbackPractice, SoftSkillProgress, TrackingLog,
    PracticeStatus
)
from app.schemas import (
    PracticeStartRequest, PracticeSubmitRequest,
    PracticeSessionResponse, PracticeResultResponse,
    SoftSkillProgressResponse, UserProgressSummary
)
from app.services.feedback_service import feedback_llm_service
from app.services.event_service import event_bus_service

logger = logging.getLogger(__name__)


class PracticeService:
    """Service for managing practice sessions"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def start_practice(self, request: PracticeStartRequest) -> PracticeSessionResponse:
        """Start a new practice session"""
        try:
            # Validate soft skill exists
            soft_skill = self.session.get(SoftSkill, request.soft_skill_id)
            if not soft_skill or not soft_skill.is_active:
                raise ValueError(f"Soft skill {request.soft_skill_id} not found or inactive")
            
            # Validate scenario exists and belongs to the soft skill
            scenario = self.session.get(SoftSkillScenario, request.scenario_id)
            if not scenario or not scenario.is_active or scenario.soft_skill_id != request.soft_skill_id:
                raise ValueError(f"Scenario {request.scenario_id} not found or invalid")
            
            # Create new practice session
            practice = PracticeTracking(
                user_id=request.user_id,
                soft_skill_id=request.soft_skill_id,
                scenario_id=request.scenario_id,
                status=PracticeStatus.STARTED
            )
            
            self.session.add(practice)
            self.session.commit()
            self.session.refresh(practice)
            
            # Log the event
            await self._log_practice_event(
                practice.session_id,
                request.user_id,
                "practice_started",
                {
                    "soft_skill_id": request.soft_skill_id,
                    "scenario_id": request.scenario_id
                }
            )
            
            # Publish event to event bus
            await event_bus_service.publish_practice_started(
                request.user_id,
                practice.session_id,
                request.soft_skill_id,
                request.scenario_id
            )
            
            logger.info(f"Practice session started: {practice.session_id}")
            
            return PracticeSessionResponse(
                session_id=practice.session_id,
                user_id=practice.user_id,
                soft_skill=self._map_soft_skill_response(soft_skill),
                scenario=self._map_scenario_response(scenario),
                status=practice.status,
                started_at=practice.started_at
            )
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error starting practice: {e}")
            raise
    
    async def submit_practice(self, request: PracticeSubmitRequest) -> PracticeResultResponse:
        """Submit and complete a practice session"""
        try:
            # Get practice session
            statement = select(PracticeTracking).where(
                PracticeTracking.session_id == request.session_id
            )
            practice = self.session.exec(statement).first()
            
            if not practice:
                raise ValueError(f"Practice session {request.session_id} not found")
            
            if practice.status != PracticeStatus.STARTED:
                raise ValueError(f"Practice session {request.session_id} is not active")
            
            # Get related entities
            soft_skill = self.session.get(SoftSkill, practice.soft_skill_id)
            scenario = self.session.get(SoftSkillScenario, practice.scenario_id)
            
            # Calculate scores (this would typically involve AI analysis)
            scores = await self._calculate_scores(
                request.user_input, 
                soft_skill.name, 
                scenario.description
            )
            
            # Update practice with results
            practice.status = PracticeStatus.COMPLETED
            practice.user_input = request.user_input
            practice.duration_seconds = request.duration_seconds
            practice.clarity_score = scores["clarity_score"]
            practice.empathy_score = scores["empathy_score"]
            practice.assertiveness_score = scores["assertiveness_score"]
            practice.listening_score = scores["listening_score"]
            practice.confidence_score = scores["confidence_score"]
            practice.overall_score = scores["overall_score"]
            practice.points_earned = self._calculate_points(scores)
            practice.completed_at = datetime.utcnow()
            
            # Generate feedback using LLM service
            feedback_data = await feedback_llm_service.generate_feedback(
                soft_skill.name,
                scenario.description,
                request.user_input,
                scores
            )
            
            # Create feedback record
            feedback = FeedbackPractice(
                practice_id=practice.id,
                overall_feedback=feedback_data["overall_feedback"],
                clarity_feedback=feedback_data["clarity_feedback"],
                empathy_feedback=feedback_data["empathy_feedback"],
                assertiveness_feedback=feedback_data["assertiveness_feedback"],
                listening_feedback=feedback_data["listening_feedback"],
                confidence_feedback=feedback_data["confidence_feedback"],
                improvement_areas=feedback_data["improvement_areas"],
                llm_model_used=feedback_data["llm_model_used"],
                llm_response_time_ms=feedback_data["response_time_ms"]
            )
            
            self.session.add(feedback)
            self.session.commit()
            self.session.refresh(practice)
            
            # Update user progress
            await self._update_user_progress(practice.user_id, practice.soft_skill_id)
            
            # Log completion event
            await self._log_practice_event(
                practice.session_id,
                practice.user_id,
                "practice_completed",
                {
                    "overall_score": practice.overall_score,
                    "points_earned": practice.points_earned,
                    "duration_seconds": practice.duration_seconds
                }
            )
            
            # Publish completion event to event bus
            await event_bus_service.publish_practice_completed(
                practice.user_id,
                practice.session_id,
                practice.soft_skill_id,
                practice.scenario_id,
                practice.overall_score,
                practice.points_earned,
                practice.duration_seconds
            )
            
            logger.info(f"Practice session completed: {practice.session_id}")
            
            return PracticeResultResponse(
                session_id=practice.session_id,
                status=practice.status,
                scores={
                    "clarity_score": practice.clarity_score,
                    "empathy_score": practice.empathy_score,
                    "assertiveness_score": practice.assertiveness_score,
                    "listening_score": practice.listening_score,
                    "confidence_score": practice.confidence_score,
                    "overall_score": practice.overall_score
                },
                feedback={
                    "overall_feedback": feedback.overall_feedback,
                    "clarity_feedback": feedback.clarity_feedback,
                    "empathy_feedback": feedback.empathy_feedback,
                    "assertiveness_feedback": feedback.assertiveness_feedback,
                    "listening_feedback": feedback.listening_feedback,
                    "confidence_feedback": feedback.confidence_feedback,
                    "improvement_areas": feedback.improvement_areas
                },
                points_earned=practice.points_earned,
                duration_seconds=practice.duration_seconds,
                completed_at=practice.completed_at
            )
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error submitting practice: {e}")
            raise
    
    async def get_user_progress(self, user_id: str) -> UserProgressSummary:
        """Get comprehensive user progress across all soft skills"""
        try:
            # Get all progress records for user
            statement = select(SoftSkillProgress).where(
                SoftSkillProgress.user_id == user_id
            )
            progress_records = self.session.exec(statement).all()
            
            total_points = sum(p.total_points for p in progress_records)
            total_completed = sum(p.completed_practices for p in progress_records)
            
            # Get improvement areas from recent practices
            recent_feedback_statement = select(FeedbackPractice).join(
                PracticeTracking
            ).where(
                PracticeTracking.user_id == user_id,
                PracticeTracking.completed_at >= datetime.utcnow() - timedelta(days=30)
            ).limit(10)
            
            recent_feedback = self.session.exec(recent_feedback_statement).all()
            improvement_areas = []
            for feedback in recent_feedback:
                improvement_areas.extend(feedback.improvement_areas)
            
            # Remove duplicates and get most common
            improvement_areas = list(set(improvement_areas))[:5]
            
            soft_skills_progress = []
            for progress in progress_records:
                soft_skill = self.session.get(SoftSkill, progress.soft_skill_id)
                if soft_skill:
                    soft_skills_progress.append(
                        SoftSkillProgressResponse(
                            soft_skill=self._map_soft_skill_response(soft_skill, progress),
                            metrics={
                                "total_practices": progress.total_practices,
                                "completed_practices": progress.completed_practices,
                                "average_score": progress.average_score,
                                "progress_percentage": progress.progress_percentage,
                                "total_points": progress.total_points,
                                "best_scores": {
                                    "clarity_score": progress.best_clarity_score,
                                    "empathy_score": progress.best_empathy_score,
                                    "assertiveness_score": progress.best_assertiveness_score,
                                    "listening_score": progress.best_listening_score,
                                    "confidence_score": progress.best_confidence_score
                                }
                            },
                            first_practice_at=progress.first_practice_at,
                            last_practice_at=progress.last_practice_at
                        )
                    )
            
            return UserProgressSummary(
                user_id=user_id,
                total_points=total_points,
                total_completed_practices=total_completed,
                soft_skills_progress=soft_skills_progress,
                improvement_areas=improvement_areas
            )
            
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            raise
    
    async def _calculate_scores(self, user_input: str, soft_skill_name: str, scenario: str) -> Dict[str, Any]:
        """Calculate practice scores (placeholder - would use AI analysis)"""
        # This is a simplified scoring system
        # In a real implementation, this would use NLP/AI to analyze the response
        
        base_score = 3  # Base score
        input_length = len(user_input.split())
        
        # Simple heuristics (replace with actual AI analysis)
        clarity_score = min(5, max(1, base_score + (1 if input_length > 20 else 0)))
        empathy_score = min(5, max(1, base_score + (1 if "understand" in user_input.lower() else 0)))
        assertiveness_score = min(5, max(1, base_score + (1 if "I" in user_input else 0)))
        listening_score = min(5, max(1, base_score + (1 if "?" in user_input else 0)))
        confidence_score = min(5, max(1, base_score + random.choice([-1, 0, 1])))
        
        overall_score = (clarity_score + empathy_score + assertiveness_score + 
                        listening_score + confidence_score) / 5
        
        return {
            "clarity_score": clarity_score,
            "empathy_score": empathy_score,
            "assertiveness_score": assertiveness_score,
            "listening_score": listening_score,
            "confidence_score": confidence_score,
            "overall_score": round(overall_score, 1)
        }
    
    def _calculate_points(self, scores: Dict[str, Any]) -> int:
        """Calculate points earned based on scores"""
        base_points = 10
        bonus_multiplier = scores["overall_score"] / 3.0
        return int(base_points * bonus_multiplier)
    
    async def _update_user_progress(self, user_id: str, soft_skill_id: int):
        """Update user progress for a specific soft skill"""
        try:
            # Get or create progress record
            statement = select(SoftSkillProgress).where(
                SoftSkillProgress.user_id == user_id,
                SoftSkillProgress.soft_skill_id == soft_skill_id
            )
            progress = self.session.exec(statement).first()
            
            if not progress:
                progress = SoftSkillProgress(
                    user_id=user_id,
                    soft_skill_id=soft_skill_id
                )
                self.session.add(progress)
            
            # Get all practices for this user and skill
            practices_statement = select(PracticeTracking).where(
                PracticeTracking.user_id == user_id,
                PracticeTracking.soft_skill_id == soft_skill_id
            )
            practices = self.session.exec(practices_statement).all()
            
            completed_practices = [p for p in practices if p.status == PracticeStatus.COMPLETED]
            
            if completed_practices:
                # Update metrics
                progress.total_practices = len(practices)
                progress.completed_practices = len(completed_practices)
                
                # Calculate average score
                scores = [p.overall_score for p in completed_practices if p.overall_score]
                progress.average_score = sum(scores) / len(scores) if scores else None
                
                # Calculate progress percentage (based on completed practices)
                # Assuming 10 practices = 100% (this could be configurable)
                max_practices_for_100_percent = 10
                progress.progress_percentage = min(100.0, 
                    (progress.completed_practices / max_practices_for_100_percent) * 100)
                
                # Update total points
                progress.total_points = sum(p.points_earned for p in completed_practices)
                
                # Update best scores
                progress.best_clarity_score = max((p.clarity_score for p in completed_practices if p.clarity_score), default=None)
                progress.best_empathy_score = max((p.empathy_score for p in completed_practices if p.empathy_score), default=None)
                progress.best_assertiveness_score = max((p.assertiveness_score for p in completed_practices if p.assertiveness_score), default=None)
                progress.best_listening_score = max((p.listening_score for p in completed_practices if p.listening_score), default=None)
                progress.best_confidence_score = max((p.confidence_score for p in completed_practices if p.confidence_score), default=None)
                
                # Update timestamps
                if not progress.first_practice_at:
                    progress.first_practice_at = min(p.started_at for p in practices)
                progress.last_practice_at = max(p.completed_at for p in completed_practices if p.completed_at)
            
            progress.updated_at = datetime.utcnow()
            self.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating user progress: {e}")
            raise
    
    async def _log_practice_event(self, session_id: str, user_id: str, event_type: str, metadata: Dict[str, Any]):
        """Log practice events for analytics"""
        try:
            log = TrackingLog(
                user_id=user_id,
                practice_session_id=session_id,
                event_type=event_type,
                event_data=metadata
            )
            self.session.add(log)
            self.session.commit()
        except Exception as e:
            logger.warning(f"Failed to log event: {e}")
    
    def _map_soft_skill_response(self, soft_skill: SoftSkill, progress: Optional[SoftSkillProgress] = None):
        """Map SoftSkill model to response schema"""
        return {
            "id": soft_skill.id,
            "name": soft_skill.name,
            "description": soft_skill.description,
            "category": soft_skill.category,
            "icon_name": soft_skill.icon_name,
            "color_theme": soft_skill.color_theme,
            "progress_percentage": progress.progress_percentage if progress else 0.0,
            "total_points": progress.total_points if progress else 0
        }
    
    def _map_scenario_response(self, scenario: SoftSkillScenario):
        """Map SoftSkillScenario model to response schema"""
        return {
            "id": scenario.id,
            "title": scenario.title,
            "description": scenario.description,
            "difficulty_level": scenario.difficulty_level,
            "estimated_duration_minutes": scenario.estimated_duration_minutes,
            "is_popular": scenario.is_popular
        }
