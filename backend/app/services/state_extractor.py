import re
from typing import Optional, Dict, Any
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState
)

class EnvironmentalStateExtractor:
    """
    Extracts structured environmental variables from both natural language queries
    and structured JSON representations.
    Maintains multi-turn context by supporting state merging.
    """

    CROP_PATTERNS = [
        "wheat", "rice", "cotton", "maize", "corn", "soybean", "sugarcane",
        "millet", "sorghum", "chickpea", "pigeonpea", "groundnut", "mustard",
        "coffee", "tea", "rubber", "barley", "pulses"
    ]

    REGION_PATTERNS = [
        r"semi-arid\s+karnataka",
        r"karnataka",
        r"semi-arid\s+deccan",
        r"semi-arid",
        r"arid\s+zone",
        r"arid",
        r"drylands",
        r"indo-gangetic\s+plains?",
        r"western\s+ghats",
        r"vidarbha",
        r"marathwada",
        r"telangana",
        r"rajasthan",
        r"sahel",
        r"mediterranean"
    ]

    def extract_from_json(self, raw_json: Dict[str, Any]) -> EnvironmentalState:
        """Parses a structured dictionary directly into an EnvironmentalState model."""
        try:
            # Check if fields are nested or flat
            if any(k in raw_json for k in ["soil", "land", "biodiversity", "climate", "human_impact"]):
                return EnvironmentalState(**raw_json)

            # Flattened or hybrid structure mapping
            soil_data = raw_json.get("soil", {})
            land_data = raw_json.get("land", {})
            bio_data = raw_json.get("biodiversity", {})
            clim_data = raw_json.get("climate", {})
            hum_data = raw_json.get("human_impact", {})

            # Map top-level shortcuts if provided directly
            if "region" in raw_json and "region" not in land_data:
                land_data["region"] = raw_json["region"]
            if "crop" in raw_json and "crop" not in land_data:
                land_data["crop"] = raw_json["crop"]
            if "organic_carbon" in raw_json and "organic_carbon_pct" not in soil_data:
                soil_data["organic_carbon_pct"] = raw_json["organic_carbon"]
            if "organic_carbon_pct" in raw_json:
                soil_data["organic_carbon_pct"] = raw_json["organic_carbon_pct"]
            if "rainfall" in raw_json and "rainfall" not in clim_data:
                clim_data["rainfall"] = raw_json["rainfall"]

            return EnvironmentalState(
                soil=SoilState(**soil_data),
                land=LandState(**land_data),
                biodiversity=BiodiversityState(**bio_data),
                climate=ClimateState(**clim_data),
                human_impact=HumanImpactState(**hum_data)
            )
        except Exception:
            return EnvironmentalState()

    def extract_from_text(self, text: str) -> EnvironmentalState:
        """
        Extracts environmental variables across all 5 classes from natural language text
        using regular expressions and domain entity mapping.
        """
        lower_text = text.lower()
        soil = SoilState()
        land = LandState()
        bio = BiodiversityState()
        climate = ClimateState()
        human = HumanImpactState()

        # 1. Soil Organic Carbon (SOC)
        # Matches: "organic carbon is 0.3%", "SOC = 0.3", "0.3% carbon", "SOC 0.3%"
        soc_match = re.search(r"(?:organic\s+carbon|soc|soil\s+carbon)(?:\s*(?:is|=|:)?\s*|\s+of\s+)(\d+(?:\.\d+)?)\s*%", lower_text)
        if not soc_match:
            soc_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:organic\s+carbon|soc)", lower_text)
        if not soc_match:
            soc_match = re.search(r"(?:organic\s+carbon|soc)(?:\s*(?:is|=|:)?\s*)(\d+(?:\.\d+)?)", lower_text)
        if soc_match:
            try:
                soil.organic_carbon_pct = float(soc_match.group(1))
            except (ValueError, IndexError):
                pass

        # Soil pH
        # Matches: "ph is 6.5", "ph 6.5", "ph: 7.2"
        ph_match = re.search(r"\bph\b(?:\s*(?:is|=|:)?\s*)(\d+(?:\.\d+)?)", lower_text)
        if ph_match:
            try:
                val = float(ph_match.group(1))
                if 0.0 <= val <= 14.0:
                    soil.ph = val
            except (ValueError, IndexError):
                pass

        # Soil moisture
        # Matches: "moisture 18%", "soil moisture is 22%"
        moisture_match = re.search(r"(?:soil\s+)?moisture(?:\s*(?:is|=|:)?\s*)(\d+(?:\.\d+)?)\s*%", lower_text)
        if moisture_match:
            try:
                soil.moisture_pct = float(moisture_match.group(1))
            except (ValueError, IndexError):
                pass

        # Soil texture
        for texture_kw in ["sandy loam", "clay loam", "silty clay", "sandy", "clay", "loam", "black soil", "red soil"]:
            if texture_kw in lower_text:
                soil.texture = texture_kw
                break

        # 2. Land Use & Crop
        for region_regex in self.REGION_PATTERNS:
            match = re.search(r"\b(" + region_regex + r")\b", lower_text, re.IGNORECASE)
            if match:
                # Format nicely
                land.region = match.group(0).strip().title()
                break

        for crop in self.CROP_PATTERNS:
            if re.search(r"\b" + crop + r"\b", lower_text):
                land.crop = crop.capitalize()
                break

        if "monoculture" in lower_text or "single crop" in lower_text:
            land.land_use = "monoculture"
            land.is_monoculture = True
        elif "agroforestry" in lower_text:
            land.land_use = "agroforestry"
            land.is_monoculture = False
        elif "polyculture" in lower_text or "intercropping" in lower_text:
            land.land_use = "polyculture"
            land.is_monoculture = False

        if "tree cover" in lower_text:
            tc_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:tree\s+cover|canopy)", lower_text)
            if tc_match:
                land.tree_cover_pct = float(tc_match.group(1))

        if "habitat fragmentation" in lower_text or "fragmented" in lower_text:
            if "high" in lower_text or "severe" in lower_text:
                land.habitat_fragmentation = "high"
            elif "medium" in lower_text or "moderate" in lower_text:
                land.habitat_fragmentation = "medium"
            else:
                land.habitat_fragmentation = "low"

        # 3. Climate
        if "rainfall" in lower_text or "rain" in lower_text:
            if re.search(r"\b(low|scanty|deficient|scarce|erratic|poor)\b.*?\brainfall\b", lower_text) or \
               re.search(r"\brainfall\b.*?\b(low|scanty|scarce|limited)\b", lower_text):
                climate.rainfall = "low"
            elif re.search(r"\b(high|heavy|abundant)\b.*?\brainfall\b", lower_text):
                climate.rainfall = "high"
            elif re.search(r"\b(medium|moderate|normal)\b.*?\brainfall\b", lower_text):
                climate.rainfall = "medium"

        if not climate.rainfall and ("semi-arid" in lower_text or "arid" in lower_text or "drought" in lower_text):
            climate.rainfall = "low"

        if "drought" in lower_text:
            if "frequent" in lower_text or "chronic" in lower_text:
                climate.drought_frequency = "frequent"
            else:
                climate.drought_frequency = "occasional"

        # Temperature
        temp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:°c|celsius|degrees)", lower_text)
        if temp_match:
            climate.temperature_celsius = float(temp_match.group(1))

        # 4. Biodiversity
        if "biodiversity is declining" in lower_text or "declining biodiversity" in lower_text or \
           "low biodiversity" in lower_text or "poor biodiversity" in lower_text:
            bio.species_richness = "low"
            bio.habitat_diversity = "low"

        if "pollinator" in lower_text or "bees" in lower_text:
            if "rare" in lower_text or "declining" in lower_text or "absent" in lower_text or "few" in lower_text:
                bio.pollinator_presence = "rare"
            elif "active" in lower_text or "abundant" in lower_text:
                bio.pollinator_presence = "active"
            else:
                bio.pollinator_presence = "moderate"

        # 5. Human Impact
        if "pesticide" in lower_text:
            if "high" in lower_text or "heavy" in lower_text or "intensive" in lower_text:
                human.pesticide_use = "high"
            elif "low" in lower_text or "minimal" in lower_text:
                human.pesticide_use = "low"
            elif "none" in lower_text or "zero" in lower_text or "organic" in lower_text:
                human.pesticide_use = "none"

        if "groundwater" in lower_text or "water extraction" in lower_text:
            if "depleted" in lower_text or "critical" in lower_text or "excessive" in lower_text:
                human.water_extraction = "critical"

        return EnvironmentalState(
            soil=soil,
            land=land,
            biodiversity=bio,
            climate=climate,
            human_impact=human
        )

    def merge_states(self, base_state: EnvironmentalState, updates: EnvironmentalState) -> EnvironmentalState:
        """
        Merges newly extracted variables into an existing state representation without
        erasing previously collected parameters (multi-turn conversational memory).
        """
        merged_soil = base_state.soil.model_dump()
        for k, v in updates.soil.model_dump().items():
            if v is not None:
                merged_soil[k] = v

        merged_land = base_state.land.model_dump()
        for k, v in updates.land.model_dump().items():
            if v is not None:
                merged_land[k] = v

        merged_bio = base_state.biodiversity.model_dump()
        for k, v in updates.biodiversity.model_dump().items():
            if v is not None:
                merged_bio[k] = v

        merged_clim = base_state.climate.model_dump()
        for k, v in updates.climate.model_dump().items():
            if v is not None:
                merged_clim[k] = v

        merged_hum = base_state.human_impact.model_dump()
        for k, v in updates.human_impact.model_dump().items():
            if v is not None:
                merged_hum[k] = v

        return EnvironmentalState(
            soil=SoilState(**merged_soil),
            land=LandState(**merged_land),
            biodiversity=BiodiversityState(**merged_bio),
            climate=ClimateState(**merged_clim),
            human_impact=HumanImpactState(**merged_hum)
        )

    def extract_state(
        self,
        user_text: Optional[str] = None,
        structured_state: Optional[Dict[str, Any]] = None,
        previous_state: Optional[EnvironmentalState] = None
    ) -> EnvironmentalState:
        """
        Unified extraction pipeline:
        Combines structured JSON, natural language text, and previous turn state.
        """
        extracted = EnvironmentalState()
        if structured_state:
            extracted = self.extract_from_json(structured_state)
        if user_text:
            text_extracted = self.extract_from_text(user_text)
            extracted = self.merge_states(extracted, text_extracted)
        if previous_state:
            extracted = self.merge_states(previous_state, extracted)
        return extracted

state_extractor = EnvironmentalStateExtractor()
