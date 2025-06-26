import httpx
import logging
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class FeedbackLLMService:
    """Service to interact with external LLM for generating feedback"""
    
    def __init__(self):
        self.base_url = settings.feedback_llm_service_url
        self.timeout = 30.0
    
    async def generate_feedback(
        self,
        soft_skill_name: str,
        scenario_description: str,
        user_input: str,
        scores: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Generate feedback using external LLM service
        
        Args:
            soft_skill_name: Name of the soft skill being practiced
            scenario_description: Description of the scenario
            user_input: User's response/approach to the scenario
            scores: Dictionary with individual metric scores
            
        Returns:
            Dictionary containing feedback and improvement areas
        """
        try:
            payload = {
                "soft_skill": soft_skill_name,
                "scenario": scenario_description,
                "user_response": user_input,
                "scores": scores,
                "language": "es",  # Spanish as default based on UI
                "feedback_style": "constructive"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/generate-feedback",
                    json=payload
                )
                response.raise_for_status()
                
                feedback_data = response.json()
                logger.info(f"Feedback generated successfully for skill: {soft_skill_name}")
                
                return {
                    "overall_feedback": feedback_data.get("overall_feedback", ""),
                    "clarity_feedback": feedback_data.get("clarity_feedback"),
                    "empathy_feedback": feedback_data.get("empathy_feedback"),
                    "assertiveness_feedback": feedback_data.get("assertiveness_feedback"),
                    "listening_feedback": feedback_data.get("listening_feedback"),
                    "confidence_feedback": feedback_data.get("confidence_feedback"),
                    "improvement_areas": feedback_data.get("improvement_areas", []),
                    "llm_model_used": feedback_data.get("model_used", "unknown"),
                    "response_time_ms": feedback_data.get("response_time_ms")
                }
                
        except httpx.TimeoutException:
            logger.error("Timeout while calling LLM service")
            return self._get_fallback_feedback(soft_skill_name, scores)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling LLM service: {e.response.status_code}")
            return self._get_fallback_feedback(soft_skill_name, scores)
        except Exception as e:
            logger.error(f"Unexpected error calling LLM service: {e}")
            return self._get_fallback_feedback(soft_skill_name, scores)
    
    def _get_fallback_feedback(self, soft_skill_name: str, scores: Dict[str, int]) -> Dict[str, Any]:
        """Provide fallback feedback when LLM service is unavailable"""
        
        overall_score = sum(scores.values()) / len(scores) if scores else 3
        
        if overall_score >= 4:
            feedback = f"¡Excelente trabajo practicando {soft_skill_name}! Has demostrado un muy buen manejo de esta habilidad."
        elif overall_score >= 3:
            feedback = f"Buen trabajo practicando {soft_skill_name}. Hay algunas áreas que puedes seguir mejorando."
        else:
            feedback = f"Has dado un buen primer paso practicando {soft_skill_name}. Con más práctica podrás mejorar significativamente."
        
        improvement_areas = []
        if scores.get("clarity_score", 5) < 3:
            improvement_areas.append("Refine message clarity")
        if scores.get("empathy_score", 5) < 3:
            improvement_areas.append("Enhance active listening")
        if scores.get("assertiveness_score", 5) < 3:
            improvement_areas.append("Improve tone control")
        if scores.get("confidence_score", 5) < 3:
            improvement_areas.append("Build confidence")
        
        return {
            "overall_feedback": feedback,
            "clarity_feedback": None,
            "empathy_feedback": None,
            "assertiveness_feedback": None,
            "listening_feedback": None,
            "confidence_feedback": None,
            "improvement_areas": improvement_areas,
            "llm_model_used": "fallback",
            "response_time_ms": None
        }


# Singleton instance
feedback_llm_service = FeedbackLLMService()
