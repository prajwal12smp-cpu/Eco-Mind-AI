import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.session import SessionLocal, engine
from backend.app.database.base import Base

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "EcoMind AI"
    assert data["knowledge_corpus_documents"] >= 6

def test_chat_sparse_input_triggers_clarifying_questions():
    payload = {
        "message": "Biodiversity is dropping rapidly on my farm and pollinators are disappearing."
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["is_information_complete"] is False
    assert len(data["clarifying_questions"]) > 0
    assert len(data["recommendations"]) == 0
    assert "critical missing parameters" in data["message"].lower()

def test_chat_complete_benchmark_turn_with_rag_and_claim_safety():
    payload = {
        "message": "My farm is in semi-arid Karnataka. Soil organic carbon is 0.3%, rainfall is low, and I cultivate wheat in monoculture with synthetic fertilizer."
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["is_information_complete"] is True
    assert len(data["clarifying_questions"]) == 0
    assert len(data["recommendations"]) >= 3
    assert len(data["multi_metric_stressors"]) >= 2
    assert len(data["detected_interactions"]) >= 1

    # Verify extracted state
    state = data["extracted_state"]
    assert state["soil"]["organic_carbon_pct"] == 0.3
    assert "karnataka" in state["land"]["region"].lower()
    assert state["land"]["crop"].lower() == "wheat"

    # Verify RAG trace and scientific grounding
    trace = data["retrieval_trace"]
    assert trace is not None
    assert len(trace["sources"]) > 0

    first_rec = data["recommendations"][0]
    assert len(first_rec["evidence"]) > 0
    # Citations must be from authorized institutions (FAO, ICRISAT, ICRAF, IPCC)
    evidence_orgs = [ev["organization"] for ev in first_rec["evidence"]]
    assert any(any(token in org for token in ["FAO", "ICRISAT", "ICRAF", "IPCC"]) for org in evidence_orgs)

def test_chat_multi_turn_conversational_constraint_adaptation():
    # Turn 1: Establish baseline farm state
    turn1_payload = {
        "message": "My farm is in semi-arid Karnataka. Soil organic carbon is 0.3%, rainfall is low, and I cultivate wheat in monoculture."
    }
    turn1_resp = client.post("/api/chat", json=turn1_payload)
    assert turn1_resp.status_code == 200
    conv_id = turn1_resp.json()["conversation_id"]

    # Turn 2: User applies a hard real-world constraint in the same conversation
    turn2_payload = {
        "conversation_id": conv_id,
        "message": "What if I cannot change my main crop due to local grain contracts?"
    }
    turn2_resp = client.post("/api/chat", json=turn2_payload)
    assert turn2_resp.status_code == 200
    turn2_data = turn2_resp.json()

    # Verify multi-turn conversational memory preserved earlier variables
    state = turn2_data["extracted_state"]
    assert state["soil"]["organic_carbon_pct"] == 0.3
    assert "karnataka" in state["land"]["region"].lower()
    assert state["land"]["crop"].lower() == "wheat"

    # Verify recommendations respect constraint: do not replace wheat, but integrate legumes/shelterbelts
    directives = [r["directive"].lower() for r in turn2_data["recommendations"]]
    assert any("strip" in d or "boundary" in d or "intercrop" in d for d in directives)

def test_land_profile_crud_and_dashboard():
    # Create Land Profile
    profile_payload = {
        "name": "Raichur Dryland Farm",
        "region": "semi-arid Karnataka",
        "primary_crop": "Wheat",
        "farming_system": "Monoculture",
        "area_hectares": 8.0,
        "initial_state": {
            "soil": {"organic_carbon_pct": 0.35, "ph": 7.9},
            "climate": {"rainfall": "low", "annual_rainfall_mm": 480.0},
            "land": {"region": "semi-arid Karnataka", "crop": "Wheat", "land_use": "Monoculture"}
        }
    }
    create_resp = client.post("/api/land-profiles", json=profile_payload)
    assert create_resp.status_code == 201
    profile = create_resp.json()
    profile_id = profile["id"]
    assert profile["name"] == "Raichur Dryland Farm"

    # Fetch List
    list_resp = client.get("/api/land-profiles")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Fetch Profile Dashboard
    dash_resp = client.get(f"/api/land-profiles/{profile_id}/dashboard")
    assert dash_resp.status_code == 200
    dashboard = dash_resp.json()
    assert dashboard["land_id"] == profile_id
    assert dashboard["metrics"]["soil"]["organic_carbon_pct"] == 0.35
    assert len(dashboard["active_stressors"]) >= 1

def test_knowledge_base_endpoints():
    # Test Search
    search_resp = client.get("/api/knowledge/search?query=nitrogen+fixation+legumes&region=semi-arid")
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert len(search_data["sources"]) > 0
    assert search_data["top_score"] is not None

    # Test Documents Catalog
    docs_resp = client.get("/api/knowledge/documents")
    assert docs_resp.status_code == 200
    docs_data = docs_resp.json()
    assert docs_data["total_documents"] >= 6

def test_standalone_recommendation_analysis():
    payload = {
        "soil": {"organic_carbon_pct": 0.28, "moisture_pct": 12.0},
        "climate": {"rainfall": "low", "drought_frequency": "high"},
        "land": {"region": "semi-arid", "crop": "Wheat", "is_monoculture": True}
    }
    response = client.post("/api/recommendations/analyze", json=payload)
    assert response.status_code == 200
    recs = response.json()
    assert len(recs) >= 2
    assert recs[0]["directive"] is not None
    assert len(recs[0]["evidence"]) > 0
