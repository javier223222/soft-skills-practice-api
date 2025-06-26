import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import SoftSkill, SoftSkillScenario, SoftSkillCategory


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden dependencies"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_soft_skill")
def sample_soft_skill_fixture(session: Session):
    """Create a sample soft skill for testing"""
    soft_skill = SoftSkill(
        name="Test Skill",
        description="A test skill for unit testing",
        category=SoftSkillCategory.COMMUNICATION,
        icon_name="test_icon",
        color_theme="blue"
    )
    session.add(soft_skill)
    session.commit()
    session.refresh(soft_skill)
    return soft_skill


@pytest.fixture(name="sample_scenario")
def sample_scenario_fixture(session: Session, sample_soft_skill: SoftSkill):
    """Create a sample scenario for testing"""
    scenario = SoftSkillScenario(
        soft_skill_id=sample_soft_skill.id,
        title="Test Scenario",
        description="A test scenario for unit testing",
        difficulty_level=3,
        estimated_duration_minutes=15,
        is_popular=True
    )
    session.add(scenario)
    session.commit()
    session.refresh(scenario)
    return scenario


def test_read_root(client: TestClient):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Soft Skill Practice Service"
    assert data["status"] == "running"


def test_health_check(client: TestClient):
    """Test the health check endpoint"""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data


def test_get_soft_skills(client: TestClient, sample_soft_skill: SoftSkill):
    """Test getting all soft skills"""
    response = client.get("/soft-skills/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Skill"


def test_get_soft_skill_by_id(client: TestClient, sample_soft_skill: SoftSkill):
    """Test getting a specific soft skill"""
    response = client.get(f"/soft-skills/{sample_soft_skill.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Skill"
    assert data["id"] == sample_soft_skill.id


def test_get_scenarios_for_skill(client: TestClient, sample_soft_skill: SoftSkill, sample_scenario: SoftSkillScenario):
    """Test getting scenarios for a soft skill"""
    response = client.get(f"/soft-skills/{sample_soft_skill.id}/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Scenario"


def test_start_practice_session(client: TestClient, sample_soft_skill: SoftSkill, sample_scenario: SoftSkillScenario):
    """Test starting a practice session"""
    request_data = {
        "user_id": "test_user_123",
        "soft_skill_id": sample_soft_skill.id,
        "scenario_id": sample_scenario.id
    }
    
    response = client.post("/practice/start", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user_123"
    assert data["status"] == "started"
    assert "session_id" in data


def test_submit_practice_session(client: TestClient, sample_soft_skill: SoftSkill, sample_scenario: SoftSkillScenario):
    """Test submitting a practice session"""
    # First start a session
    start_request = {
        "user_id": "test_user_123",
        "soft_skill_id": sample_soft_skill.id,
        "scenario_id": sample_scenario.id
    }
    
    start_response = client.post("/practice/start", json=start_request)
    assert start_response.status_code == 200
    session_data = start_response.json()
    session_id = session_data["session_id"]
    
    # Submit the session
    submit_request = {
        "session_id": session_id,
        "user_input": "This is my response to the scenario. I would approach it professionally and with empathy.",
        "duration_seconds": 300
    }
    
    response = client.post("/practice/submit", json=submit_request)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["status"] == "completed"
    assert "scores" in data
    assert "feedback" in data
    assert data["points_earned"] > 0


def test_get_user_progress(client: TestClient):
    """Test getting user progress"""
    response = client.get("/progress/test_user_123")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user_123"
    assert "total_points" in data
    assert "soft_skills_progress" in data
