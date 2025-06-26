from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models import SoftSkill, SoftSkillScenario
from app.schemas import SoftSkillResponse, ScenarioResponse
from app.services.practice_service import PracticeService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/soft-skills", tags=["Soft Skills"])


@router.get("/", response_model=List[SoftSkillResponse])
async def get_soft_skills(
    user_id: str = None,
    session: Session = Depends(get_session)
):
    """Get all available soft skills with optional user progress"""
    try:
        statement = select(SoftSkill).where(SoftSkill.is_active == True)
        soft_skills = session.exec(statement).all()
        
        response = []
        for skill in soft_skills:
            # If user_id provided, include progress
            progress_percentage = 0.0
            total_points = 0
            
            if user_id:
                practice_service = PracticeService(session)
                try:
                    user_progress = await practice_service.get_user_progress(user_id)
                    skill_progress = next(
                        (sp for sp in user_progress.soft_skills_progress 
                         if sp.soft_skill.id == skill.id), 
                        None
                    )
                    if skill_progress:
                        progress_percentage = skill_progress.metrics.progress_percentage
                        total_points = skill_progress.metrics.total_points
                except Exception as e:
                    logger.warning(f"Could not get progress for user {user_id}: {e}")
            
            response.append(SoftSkillResponse(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                category=skill.category,
                icon_name=skill.icon_name,
                color_theme=skill.color_theme,
                progress_percentage=progress_percentage,
                total_points=total_points
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting soft skills: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving soft skills"
        )


@router.get("/{soft_skill_id}", response_model=SoftSkillResponse)
async def get_soft_skill(
    soft_skill_id: int,
    user_id: str = None,
    session: Session = Depends(get_session)
):
    """Get a specific soft skill by ID"""
    try:
        soft_skill = session.get(SoftSkill, soft_skill_id)
        if not soft_skill or not soft_skill.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Soft skill {soft_skill_id} not found"
            )
        
        progress_percentage = 0.0
        total_points = 0
        
        if user_id:
            practice_service = PracticeService(session)
            try:
                user_progress = await practice_service.get_user_progress(user_id)
                skill_progress = next(
                    (sp for sp in user_progress.soft_skills_progress 
                     if sp.soft_skill.id == soft_skill.id), 
                    None
                )
                if skill_progress:
                    progress_percentage = skill_progress.metrics.progress_percentage
                    total_points = skill_progress.metrics.total_points
            except Exception as e:
                logger.warning(f"Could not get progress for user {user_id}: {e}")
        
        return SoftSkillResponse(
            id=soft_skill.id,
            name=soft_skill.name,
            description=soft_skill.description,
            category=soft_skill.category,
            icon_name=soft_skill.icon_name,
            color_theme=soft_skill.color_theme,
            progress_percentage=progress_percentage,
            total_points=total_points
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting soft skill {soft_skill_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving soft skill"
        )


@router.get("/{soft_skill_id}/scenarios", response_model=List[ScenarioResponse])
async def get_scenarios_for_skill(
    soft_skill_id: int,
    include_popular_only: bool = False,
    session: Session = Depends(get_session)
):
    """Get scenarios for a specific soft skill"""
    try:
        # Verify soft skill exists
        soft_skill = session.get(SoftSkill, soft_skill_id)
        if not soft_skill or not soft_skill.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Soft skill {soft_skill_id} not found"
            )
        
        statement = select(SoftSkillScenario).where(
            SoftSkillScenario.soft_skill_id == soft_skill_id,
            SoftSkillScenario.is_active == True
        )
        
        if include_popular_only:
            statement = statement.where(SoftSkillScenario.is_popular == True)
        
        scenarios = session.exec(statement).all()
        
        return [
            ScenarioResponse(
                id=scenario.id,
                title=scenario.title,
                description=scenario.description,
                difficulty_level=scenario.difficulty_level,
                estimated_duration_minutes=scenario.estimated_duration_minutes,
                is_popular=scenario.is_popular
            )
            for scenario in scenarios
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scenarios for skill {soft_skill_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving scenarios"
        )
