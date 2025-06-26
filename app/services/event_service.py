import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.config import settings
from app.schemas import PracticeEvent, ProgressUpdateEvent

logger = logging.getLogger(__name__)


class EventBusService:
    """Service for publishing events to external event bus"""
    
    def __init__(self):
        self.event_bus_url = settings.event_bus_url
        self.timeout = 10.0
        self.enabled = bool(self.event_bus_url)
    
    async def publish_practice_started(
        self, 
        user_id: str, 
        session_id: str, 
        soft_skill_id: int, 
        scenario_id: int
    ):
        """Publish practice started event"""
        if not self.enabled:
            return
        
        event = PracticeEvent(
            event_type="practice_started",
            user_id=user_id,
            session_id=session_id,
            soft_skill_id=soft_skill_id,
            scenario_id=scenario_id,
            timestamp=datetime.utcnow(),
            metadata={
                "source": "soft_skill_practice_service",
                "version": "1.0.0"
            }
        )
        
        await self._publish_event("practice.started", event.dict())
    
    async def publish_practice_completed(
        self, 
        user_id: str, 
        session_id: str, 
        soft_skill_id: int, 
        scenario_id: int,
        overall_score: float,
        points_earned: int,
        duration_seconds: int
    ):
        """Publish practice completed event"""
        if not self.enabled:
            return
        
        event = PracticeEvent(
            event_type="practice_completed",
            user_id=user_id,
            session_id=session_id,
            soft_skill_id=soft_skill_id,
            scenario_id=scenario_id,
            timestamp=datetime.utcnow(),
            metadata={
                "overall_score": overall_score,
                "points_earned": points_earned,
                "duration_seconds": duration_seconds,
                "source": "soft_skill_practice_service",
                "version": "1.0.0"
            }
        )
        
        await self._publish_event("practice.completed", event.dict())
    
    async def publish_progress_updated(
        self, 
        user_id: str, 
        soft_skill_id: int,
        previous_progress: float,
        new_progress: float,
        points_earned: int
    ):
        """Publish progress update event"""
        if not self.enabled:
            return
        
        event = ProgressUpdateEvent(
            user_id=user_id,
            soft_skill_id=soft_skill_id,
            previous_progress=previous_progress,
            new_progress=new_progress,
            points_earned=points_earned,
            timestamp=datetime.utcnow()
        )
        
        await self._publish_event("progress.updated", event.dict())
    
    async def publish_milestone_achieved(
        self, 
        user_id: str, 
        soft_skill_id: int,
        milestone_type: str,
        milestone_value: Any
    ):
        """Publish milestone achievement event"""
        if not self.enabled:
            return
        
        event = {
            "event_type": "milestone_achieved",
            "user_id": user_id,
            "soft_skill_id": soft_skill_id,
            "milestone_type": milestone_type,  # "first_practice", "10_practices", "skill_mastery", etc.
            "milestone_value": milestone_value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "source": "soft_skill_practice_service",
                "version": "1.0.0"
            }
        }
        
        await self._publish_event("milestone.achieved", event)
    
    async def _publish_event(self, topic: str, event_data: Dict[str, Any]):
        """Publish event to event bus"""
        try:
            if not self.enabled:
                logger.debug(f"Event bus disabled, skipping event: {topic}")
                return
            
            payload = {
                "topic": topic,
                "event": event_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.event_bus_url}/events/publish",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                logger.info(f"Event published successfully: {topic}")
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout publishing event to event bus: {topic}")
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error publishing event: {e.response.status_code} for topic: {topic}")
        except Exception as e:
            logger.warning(f"Unexpected error publishing event: {e} for topic: {topic}")


# Singleton instance
event_bus_service = EventBusService()
