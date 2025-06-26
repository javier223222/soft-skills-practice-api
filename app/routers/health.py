from fastapi import APIRouter, Depends
from sqlmodel import Session
from datetime import datetime

from app.database import get_session, check_database_health
from app.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("/", response_model=HealthResponse)
async def health_check(session: Session = Depends(get_session)):
    """Health check endpoint"""
    db_status = "healthy" if check_database_health() else "unhealthy"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "unhealthy",
        database=db_status,
        timestamp=datetime.utcnow()
    )
