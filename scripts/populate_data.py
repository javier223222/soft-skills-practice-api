"""
Script to populate the database with initial data matching the UI screens
"""

from sqlmodel import Session, create_engine
from app.models import SoftSkill, SoftSkillScenario, SoftSkillCategory
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def populate_initial_data():
    """Populate database with initial soft skills and scenarios"""
    
    engine = create_engine(settings.database_url)
    
    with Session(engine) as session:
        # Create soft skills matching the UI
        soft_skills_data = [
            {
                "name": "Conflict Resolution",
                "description": "Learn to analyze complex situations and find practical and creative solutions to overcome obstacles.",
                "category": SoftSkillCategory.PROBLEM_SOLVING,
                "icon_name": "conflict_resolution",
                "color_theme": "cyan"
            },
            {
                "name": "Critical Thinking",
                "description": "Develop your ability to analyze information logically and make informed decisions.",
                "category": SoftSkillCategory.PROBLEM_SOLVING,
                "icon_name": "critical_thinking",
                "color_theme": "purple"
            },
            {
                "name": "Empathy",
                "description": "Strengthen your ability to understand the emotions and perspectives of others by showing genuine interest and support.",
                "category": SoftSkillCategory.EMOTIONAL_INTELLIGENCE,
                "icon_name": "empathy",
                "color_theme": "red"
            },
            {
                "name": "Communication",
                "description": "Enhance your ability to express ideas clearly and effectively in various situations.",
                "category": SoftSkillCategory.COMMUNICATION,
                "icon_name": "communication",
                "color_theme": "blue"
            },
            {
                "name": "Leadership",
                "description": "Develop skills to guide and inspire teams towards achieving common goals.",
                "category": SoftSkillCategory.LEADERSHIP,
                "icon_name": "leadership",
                "color_theme": "green"
            },
            {
                "name": "Teamwork",
                "description": "Learn to collaborate effectively with others to achieve shared objectives.",
                "category": SoftSkillCategory.TEAMWORK,
                "icon_name": "teamwork",
                "color_theme": "orange"
            }
        ]
        
        soft_skills = []
        for skill_data in soft_skills_data:
            skill = SoftSkill(**skill_data)
            session.add(skill)
            soft_skills.append(skill)
        
        session.commit()
        
        # Refresh to get IDs
        for skill in soft_skills:
            session.refresh(skill)
        
        # Create scenarios matching the UI
        scenarios_data = [
            # Conflict Resolution scenarios
            {
                "soft_skill_name": "Conflict Resolution",
                "scenarios": [
                    {
                        "title": "Asking for a raise",
                        "description": "You need to approach your boss to discuss a salary increase. How do you prepare for this conversation and what points do you emphasize?",
                        "difficulty_level": 3,
                        "estimated_duration_minutes": 15,
                        "is_popular": True
                    },
                    {
                        "title": "Telling a classmate I didn't like their behavior",
                        "description": "A classmate has been behaving in a way that makes you uncomfortable. How do you address this situation respectfully?",
                        "difficulty_level": 2,
                        "estimated_duration_minutes": 10,
                        "is_popular": True
                    },
                    {
                        "title": "Disagreement with team member",
                        "description": "You and a team member have different opinions on how to approach a project. How do you resolve this disagreement?",
                        "difficulty_level": 3,
                        "estimated_duration_minutes": 20,
                        "is_popular": False
                    }
                ]
            },
            # Critical Thinking scenarios
            {
                "soft_skill_name": "Critical Thinking",
                "scenarios": [
                    {
                        "title": "Analyzing a complex problem",
                        "description": "Your team is facing a technical challenge that seems to have no clear solution. How do you approach problem-solving?",
                        "difficulty_level": 4,
                        "estimated_duration_minutes": 25,
                        "is_popular": True
                    },
                    {
                        "title": "Making a data-driven decision",
                        "description": "You have conflicting data points and need to make an important business decision. How do you proceed?",
                        "difficulty_level": 3,
                        "estimated_duration_minutes": 20,
                        "is_popular": False
                    }
                ]
            },
            # Empathy scenarios
            {
                "soft_skill_name": "Empathy",
                "scenarios": [
                    {
                        "title": "Supporting a struggling colleague",
                        "description": "A colleague seems overwhelmed and stressed. How do you offer support while being respectful of their situation?",
                        "difficulty_level": 2,
                        "estimated_duration_minutes": 15,
                        "is_popular": True
                    },
                    {
                        "title": "Understanding different perspectives",
                        "description": "During a team meeting, there are several different viewpoints. How do you ensure everyone feels heard?",
                        "difficulty_level": 3,
                        "estimated_duration_minutes": 20,
                        "is_popular": False
                    }
                ]
            },
            # Communication scenarios
            {
                "soft_skill_name": "Communication",
                "scenarios": [
                    {
                        "title": "Presenting to stakeholders",
                        "description": "You need to present project results to senior stakeholders. How do you communicate effectively?",
                        "difficulty_level": 4,
                        "estimated_duration_minutes": 30,
                        "is_popular": True
                    },
                    {
                        "title": "Giving constructive feedback",
                        "description": "A team member's work needs improvement. How do you provide feedback that is helpful and encouraging?",
                        "difficulty_level": 3,
                        "estimated_duration_minutes": 15,
                        "is_popular": True
                    }
                ]
            },
            # Leadership scenarios
            {
                "soft_skill_name": "Leadership",
                "scenarios": [
                    {
                        "title": "Motivating a demotivated team",
                        "description": "Your team morale is low after a failed project. How do you re-energize and motivate them?",
                        "difficulty_level": 4,
                        "estimated_duration_minutes": 25,
                        "is_popular": True
                    },
                    {
                        "title": "Delegating responsibilities",
                        "description": "You have multiple tasks and need to delegate effectively. How do you assign tasks appropriately?",
                        "difficulty_level": 3,
                        "estimated_duration_minutes": 20,
                        "is_popular": False
                    }
                ]
            },
            # Teamwork scenarios
            {
                "soft_skill_name": "Teamwork",
                "scenarios": [
                    {
                        "title": "Collaborating on a group project",
                        "description": "You're working on a group project with people from different departments. How do you ensure effective collaboration?",
                        "difficulty_level": 2,
                        "estimated_duration_minutes": 20,
                        "is_popular": True
                    },
                    {
                        "title": "Managing team conflicts",
                        "description": "Two team members are in conflict and it's affecting the team. How do you help resolve the situation?",
                        "difficulty_level": 4,
                        "estimated_duration_minutes": 30,
                        "is_popular": False
                    }
                ]
            }
        ]
        
        # Create scenarios
        for skill_scenarios in scenarios_data:
            skill_name = skill_scenarios["soft_skill_name"]
            skill = next((s for s in soft_skills if s.name == skill_name), None)
            
            if skill:
                for scenario_data in skill_scenarios["scenarios"]:
                    scenario = SoftSkillScenario(
                        soft_skill_id=skill.id,
                        **scenario_data
                    )
                    session.add(scenario)
        
        session.commit()
        logger.info("Initial data populated successfully")


if __name__ == "__main__":
    populate_initial_data()
