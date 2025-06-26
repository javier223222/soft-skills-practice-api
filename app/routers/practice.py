from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.schemas import (
    PracticeStartRequest, PracticeSubmitRequest,
    PracticeSessionResponse, PracticeResultResponse
)
from app.services.practice_service import PracticeService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/practice", tags=["Practice Sessions"])


@router.post("/start", response_model=PracticeSessionResponse)
async def start_practice_session(
    request: PracticeStartRequest,
    session: Session = Depends(get_session)
):
    """Start a new practice session"""
    try:
        practice_service = PracticeService(session)
        result = await practice_service.start_practice(request)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting practice session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting practice session"
        )


@router.post("/submit", response_model=PracticeResultResponse)
async def submit_practice_session(
    request: PracticeSubmitRequest,
    session: Session = Depends(get_session)
):
    """Submit and complete a practice session"""
    try:
        practice_service = PracticeService(session)
        result = await practice_service.submit_practice(request)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting practice session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting practice session"
        )
