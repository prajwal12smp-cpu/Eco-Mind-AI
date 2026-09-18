import pytest
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState
)
from backend.app.services.clarifying_engine import ClarifyingEngine
from backend.app.services.reasoning_engine import EnvironmentalReasoningEngine

@pytest.fixture
def clarifying_engine():
    return ClarifyingEngine()

@pytest.fixture
def reasoning_engine():
    return EnvironmentalReasoningEngine()

def test_clarifying_questions_for_sparse_input(clarifying_engine):
    # Single vague user statement: "Biodiversity is declining on my land."
    state = EnvironmentalState(
        biodiversity=BiodiversityState(species_richness="low", habitat_diversity="low")
    )
    is_complete, questions = clarifying_engine.evaluate_completeness(state)
    assert is_complete is False
    assert len(questions) > 0
    # Checks that prioritized missing variables are requested: region, crop/land use, rainfall, or SOC
    all_questions_text = " ".join(questions).lower()
    assert "region" in all_questions_text or "agro-climatic" in all_questions_text
    assert "crop" in all_questions_text or "farming system" in all_questions_text

def test_clarifying_engine_identifies_completeness_when_threshold_reached(clarifying_engine):
    # Complete benchmark scenario
    state = EnvironmentalState(
        soil=SoilState(organic_carbon_pct=0.3),
        land=LandState(region="Semi-arid Karnataka", crop="Wheat", land_use="monoculture"),
        climate=ClimateState(rainfall="low")
    )
    is_complete, questions = clarifying_engine.evaluate_completeness(state)
    assert is_complete is True
    assert len(questions) == 0

def test_multi_metric_reasoning_benchmark_scenario(reasoning_engine):
    """
    Official Challenge Benchmark Scenario:
    - Organic carbon = 0.3%
    - Rainfall = low
    - Crop = wheat
    - Land use = monoculture
    - Region = semi-arid Karnataka
    
    Verifies that system executes multi-metric reasoning across Soil, Climate, and Land:
    Low SOC + Low Rainfall + Monoculture -> Cross-variable couplings & non-obvious interventions.
    """
    state = EnvironmentalState(
        soil=SoilState(organic_carbon_pct=0.3, moisture_pct=15.0),
        land=LandState(region="Semi-arid Karnataka", crop="Wheat", land_use="monoculture"),
        climate=ClimateState(rainfall="low", drought_frequency="frequent"),
        biodiversity=BiodiversityState(species_richness="low")
    )

    result = reasoning_engine.analyze(state)

    # 1. Verify detected stressors across all 3 domains
    stressor_codes = [s.code for s in result.stressors]
    assert "ACUTE_LOW_SOC" in stressor_codes
    assert "METEOROLOGICAL_WATER_DEFICIT" in stressor_codes
    assert "MONOCULTURE_SIMPLIFICATION" in stressor_codes

    # 2. Verify cross-variable ecological couplings (Soil <-> Climate <-> Biodiversity)
    coupling_names = [c.name for c in result.cross_variable_couplings]
    assert any("Soil Organic Carbon ↔ Soil Biological Activity" in name for name in coupling_names)
    assert any("Crop Diversity ↔ Habitat Diversity" in name for name in coupling_names)

    # 3. Verify candidate interventions are non-obvious and grounded
    candidate_titles = [c.title for c in result.candidate_interventions]
    assert any("Legume Strip-Intercropping" in title for title in candidate_titles)
    assert any("Agroforestry" in title for title in candidate_titles)

    # Verify candidate addresses multiple stressors
    top_cand = result.candidate_interventions[0]
    assert len(top_cand.addresses_stressors) >= 2
    assert "Soil Organic Carbon" in top_cand.affected_metrics
    assert "Soil Moisture Retention" in top_cand.affected_metrics

def test_conversational_constraint_adaptation(reasoning_engine):
    """
    Verifies conversational adaptation when user imposes constraints:
    "What if I cannot change my main crop?"
    """
    state = EnvironmentalState(
        soil=SoilState(organic_carbon_pct=0.3),
        land=LandState(region="Semi-arid Karnataka", crop="Wheat", land_use="monoculture"),
        climate=ClimateState(rainfall="low")
    )

    result = reasoning_engine.analyze(state, user_constraints={"cannot_change_main_crop": True})
    candidate_titles = [c.title for c in result.candidate_interventions]

    # Verify that the system accommodates the constraint by offering in-situ intercropping
    # without displacing the cash crop, rather than forcing crop replacement
    assert any("Existing Wheat Rows" in title or "In-Situ" in title or "Field-Border" in title for title in candidate_titles)
