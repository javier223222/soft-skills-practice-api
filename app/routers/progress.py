from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.database import get_session
from app.schemas import (
    SoftSkillProgressResponse, UserProgressSummary
)
from app.services.practice_service import PracticeService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])


@router.get("/{user_id}", response_model=UserProgressSummary)
async def get_user_progress(
    user_id: str,
    session: Session = Depends(get_session)
):
    """Get comprehensive progress for a user across all soft skills"""
    try:
        practice_service = PracticeService(session)
        progress = await practice_service.get_user_progress(user_id)
        return progress
        
    except Exception as e:
        logger.error(f"Error getting user progress for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user progress"
        )


@router.get("/{user_id}/soft-skills/{soft_skill_id}", response_model=SoftSkillProgressResponse)
async def get_user_skill_progress(
    user_id: str,
    soft_skill_id: int,
    session: Session = Depends(get_session)
):
    """Get detailed progress for a specific soft skill"""
    try:
        practice_service = PracticeService(session)
        user_progress = await practice_service.get_user_progress(user_id)
        
        skill_progress = next(
            (sp for sp in user_progress.soft_skills_progress 
             if sp.soft_skill.id == soft_skill_id), 
            None
        )
        
        if not skill_progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No progress found for user {user_id} and skill {soft_skill_id}"
            )
        
        return skill_progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting skill progress for user {user_id}, skill {soft_skill_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving skill progress"
        )
