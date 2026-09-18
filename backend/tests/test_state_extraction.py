import pytest
from backend.app.services.state_extractor import EnvironmentalStateExtractor
from backend.app.schemas.environmental_state import EnvironmentalState

@pytest.fixture
def extractor():
    return EnvironmentalStateExtractor()

def test_extract_from_structured_json(extractor):
    raw_payload = {
        "region": "semi-arid Karnataka",
        "soil": {
            "organic_carbon_pct": 0.3,
            "ph": 6.5,
            "moisture_pct": 18.0
        },
        "climate": {
            "rainfall": "low",
            "temperature_celsius": 31.0
        },
        "land": {
            "crop": "Wheat",
            "land_use": "monoculture"
        },
        "biodiversity": {
            "species_richness": "low"
        }
    }
    state = extractor.extract_from_json(raw_payload)
    assert isinstance(state, EnvironmentalState)
    assert state.soil.organic_carbon_pct == 0.3
    assert state.soil.ph == 6.5
    assert state.climate.rainfall == "low"
    assert state.land.crop == "Wheat"
    assert state.land.land_use == "monoculture"
    assert state.biodiversity.species_richness == "low"

def test_extract_from_natural_language_benchmark(extractor):
    nl_text = "My wheat field in semi-arid Karnataka has organic carbon 0.3% and rainfall is low under monoculture."
    state = extractor.extract_from_text(nl_text)
    
    assert state.soil.organic_carbon_pct == 0.3
    assert state.land.crop == "Wheat"
    assert "Karnataka" in (state.land.region or "")
    assert state.climate.rainfall == "low"
    assert state.land.land_use == "monoculture"

def test_multi_turn_state_merging_conversational_memory(extractor):
    # Turn 1: User introduces region and general problem
    turn1_text = "Biodiversity is declining on my land in semi-arid Karnataka."
    state_turn1 = extractor.extract_from_text(turn1_text)
    assert "Karnataka" in (state_turn1.land.region or "")
    assert state_turn1.biodiversity.species_richness == "low"
    assert state_turn1.land.crop is None
    assert state_turn1.soil.organic_carbon_pct is None

    # Turn 2: User provides crop and farming system
    turn2_text = "I grow wheat under monoculture."
    state_turn2 = extractor.extract_from_text(turn2_text)
    merged_turn2 = extractor.merge_states(state_turn1, state_turn2)
    # Checks memory retention:
    assert "Karnataka" in (merged_turn2.land.region or "")
    assert merged_turn2.land.crop == "Wheat"
    assert merged_turn2.land.land_use == "monoculture"
    assert merged_turn2.biodiversity.species_richness == "low"

    # Turn 3: User provides specific soil organic carbon metric and rainfall
    turn3_text = "Organic carbon is 0.3% and rainfall is low."
    state_turn3 = extractor.extract_from_text(turn3_text)
    merged_turn3 = extractor.merge_states(merged_turn2, state_turn3)
    # Check that all variables from turns 1, 2, and 3 are intact:
    assert merged_turn3.soil.organic_carbon_pct == 0.3
    assert merged_turn3.climate.rainfall == "low"
    assert merged_turn3.land.crop == "Wheat"
    assert merged_turn3.land.land_use == "monoculture"
    assert "Karnataka" in (merged_turn3.land.region or "")
    assert merged_turn3.biodiversity.species_richness == "low"

def test_empty_and_partial_state_checks(extractor):
    empty_state = EnvironmentalState()
    assert empty_state.is_empty() is True
    assert empty_state.count_specified_variables() == 0

    partial_state = extractor.extract_from_text("Soil pH is 6.5")
    assert partial_state.is_empty() is False
    assert partial_state.soil.ph == 6.5
    assert partial_state.count_specified_variables() == 1
