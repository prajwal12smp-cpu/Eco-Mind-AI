import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.base import Base
from backend.app.models.user import User
from backend.app.models.land_profile import LandProfile
from backend.app.models.metrics import SoilMetric, ClimateMetric, BiodiversityMetric, HumanImpactMetric
from backend.app.models.recommendation import Recommendation, Source
from backend.app.models.conversation import Conversation, ConversationMessage

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_database_schema_and_relationships(db_session):
    # 1. Create User
    user = User(email="scientist@darukaa.earth")
    db_session.add(user)
    db_session.commit()

    # 2. Create LandProfile
    land = LandProfile(
        user_id=user.id,
        name="Karnataka Demo Plot 1",
        region="Semi-Arid Karnataka",
        primary_crop="Wheat",
        farming_system="Monoculture",
        area_hectares=10.5
    )
    db_session.add(land)
    db_session.commit()

    # 3. Add Soil & Climate metrics
    soil = SoilMetric(land_profile_id=land.id, organic_carbon_pct=0.3, ph=6.5, moisture_pct=18.0)
    climate = ClimateMetric(land_profile_id=land.id, rainfall_category="low", drought_frequency="frequent")
    bio = BiodiversityMetric(land_profile_id=land.id, species_richness_index="low", habitat_diversity_index="low")
    human = HumanImpactMetric(land_profile_id=land.id, pesticide_intensity="medium", water_extraction_rate="critical")
    db_session.add_all([soil, climate, bio, human])
    db_session.commit()

    # 4. Add Recommendation with grounded Source
    rec = Recommendation(
        land_profile_id=land.id,
        title="Legume Strip-Intercropping & Stubble Mulching",
        directive="Introduce chickpea or pigeonpea rows within the wheat monoculture and retain crop residue.",
        scientific_rationale="Legume symbiotic nitrogen fixation enhances microbial diversity; residue retention prevents surface evaporation.",
        impacted_metrics=["Soil organic carbon", "Soil moisture", "Habitat diversity"],
        time_horizon="Medium term",
        confidence_level="High",
        reasoning_trace=["Soil organic carbon is 0.3%", "Rainfall is scarce", "Monoculture induces habitat simplification"]
    )
    db_session.add(rec)
    db_session.commit()

    source = Source(
        recommendation_id=rec.id,
        title="Recarbonizing Global Soils: Practices for Semi-Arid Croplands",
        organization="Food and Agriculture Organization (FAO)",
        year=2020,
        document_type="report",
        evidence_snippet="Legume intercropping in semi-arid zones increases SOC by 15-25% over 2-3 years while preserving soil moisture.",
        relevance_score=0.92
    )
    db_session.add(source)
    db_session.commit()

    # 5. Add Conversation & Message
    conv = Conversation(land_profile_id=land.id)
    db_session.add(conv)
    db_session.commit()

    msg1 = ConversationMessage(
        conversation_id=conv.id,
        role="user",
        content="Biodiversity is declining on my wheat land in semi-arid Karnataka.",
        extracted_state={"soil": {"organic_carbon_pct": 0.3}}
    )
    db_session.add(msg1)
    db_session.commit()

    # Assert integrity & relational traversal
    queried_land = db_session.query(LandProfile).filter_by(id=land.id).first()
    assert queried_land is not None
    assert queried_land.region == "Semi-Arid Karnataka"
    assert len(queried_land.soil_metrics) == 1
    assert queried_land.soil_metrics[0].organic_carbon_pct == 0.3
    assert len(queried_land.recommendations) == 1
    assert len(queried_land.recommendations[0].sources) == 1
    assert queried_land.recommendations[0].sources[0].organization == "Food and Agriculture Organization (FAO)"
    assert len(queried_land.conversations) == 1
    assert len(queried_land.conversations[0].messages) == 1
