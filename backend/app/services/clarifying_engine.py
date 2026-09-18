from typing import List, Tuple
from backend.app.schemas.environmental_state import EnvironmentalState

class ClarifyingEngine:
    """
    Detects missing critical environmental variables and formulates targeted,
    high-entropy clarifying questions.
    Prioritizes questions that materially affect agroecological viability:
    1. Region & Agro-climatic zone
    2. Land use / Farming system & Crop
    3. Climate & Water availability / Rainfall
    4. Soil organic carbon (SOC) & Soil characteristics
    5. Biodiversity & Pollinator observations
    6. Human impact (pesticide application, groundwater extraction)
    """

    def evaluate_completeness(self, state: EnvironmentalState) -> Tuple[bool, List[str]]:
        """
        Determines if the environmental state contains sufficient cross-variable
        information to execute grounded multi-metric reasoning.
        Requires at least 3 distinct domains to prevent shallow single-variable answers.
        Returns: (is_complete, list_of_targeted_questions)
        """
        questions: List[str] = []

        # 1. Geographic / Agro-climatic context
        has_region = bool(state.land.region and state.land.region.strip())
        if not has_region:
            questions.append(
                "Could you specify your geographic region or agro-climatic zone (e.g., Semi-arid Karnataka, Indo-Gangetic Plain, Deccan Plateau)?"
            )

        # 2. Farming System & Crop Type
        has_crop = bool(state.land.crop and state.land.crop.strip())
        has_land_use = bool(state.land.land_use or state.land.is_monoculture is not None)
        if not has_crop or not has_land_use:
            questions.append(
                "What is your primary crop (e.g., wheat, cotton, millet) and farming system (e.g., monoculture, mixed cropping, agroforestry)?"
            )

        # 3. Climate & Water
        has_climate = bool(
            state.climate.rainfall is not None or 
            state.climate.annual_rainfall_mm is not None or 
            state.climate.water_availability is not None
        )
        if not has_climate:
            questions.append(
                "What is the prevailing rainfall pattern or water availability (e.g., low/erratic rainfall, rainfed, irrigated, frequent drought)?"
            )

        # 4. Soil Health (SOC is critical)
        has_soil = bool(
            state.soil.organic_carbon_pct is not None or 
            state.soil.ph is not None or 
            state.soil.moisture_pct is not None
        )
        if not has_soil:
            questions.append(
                "Do you have soil test data available, particularly Soil Organic Carbon (SOC %) or soil pH and texture?"
            )

        # 5. Biodiversity / Ecological baseline
        has_bio = bool(
            state.biodiversity.species_richness is not None or 
            state.biodiversity.habitat_diversity is not None or
            state.biodiversity.pollinator_presence is not None
        )
        if not has_bio and len(questions) < 3:
            questions.append(
                "Have you noticed changes in local biodiversity indicators, such as pollinator activity or native flora/fauna?"
            )

        # Decision threshold:
        # A state is considered sufficiently complete for multi-metric reasoning if:
        # - It has at least 3 domains specified (e.g. soil + climate + land)
        # - Core anchors (region or climate, plus crop or land_use) are known.
        domains_present = 0
        if state.soil.model_dump(exclude_none=True):
            domains_present += 1
        if state.land.model_dump(exclude_none=True):
            domains_present += 1
        if state.climate.model_dump(exclude_none=True):
            domains_present += 1
        if state.biodiversity.model_dump(exclude_none=True):
            domains_present += 1
        if state.human_impact.model_dump(exclude_none=True):
            domains_present += 1

        is_complete = (domains_present >= 3) and (has_region or has_climate) and (has_crop or has_land_use)

        # If complete, do not ask follow-up questions. If incomplete, return top 2-3 most critical questions.
        if is_complete:
            return True, []
        return False, questions[:3]

clarifying_engine = ClarifyingEngine()
