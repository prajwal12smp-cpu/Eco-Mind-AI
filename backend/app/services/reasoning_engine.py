from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.environmental_state import EnvironmentalState

class EnvironmentalStressor(BaseModel):
    category: str  # "soil", "climate", "land", "biodiversity", "human_impact"
    code: str
    severity: str  # "high", "moderate", "low"
    description: str
    metrics_triggering: List[str]

class CrossVariableCoupling(BaseModel):
    name: str
    mechanism: str
    variables_involved: List[str]
    ecological_risk: str

class CandidateIntervention(BaseModel):
    id: str
    title: str
    primary_category: str  # "intercropping", "agroforestry", "residue_management", "conservation_tillage"
    description: str
    addresses_stressors: List[str]
    affected_metrics: List[str]
    suitability_score: float
    time_horizon: str  # "Short term", "Medium term", "Long term"
    rationale_points: List[str]
    rag_search_query: str

class ReasoningAnalysisResult(BaseModel):
    stressors: List[EnvironmentalStressor]
    cross_variable_couplings: List[CrossVariableCoupling]
    candidate_interventions: List[CandidateIntervention]
    summary_diagnosis: str

class EnvironmentalReasoningEngine:
    """
    Deterministic Ecological Reasoning Engine.
    Models multi-variable relationships across Soil, Land, Biodiversity, Climate, and Human Impact.
    Strictly forbids single-variable hardcoding.
    """

    def analyze(self, state: EnvironmentalState, user_constraints: Optional[Dict[str, Any]] = None) -> ReasoningAnalysisResult:
        constraints = user_constraints or {}
        stressors = self._detect_stressors(state)
        couplings = self._model_couplings(state, stressors)
        candidates = self._generate_and_filter_candidates(state, stressors, couplings, constraints)

        summary_diagnosis = self._generate_diagnosis_text(state, stressors, couplings)

        return ReasoningAnalysisResult(
            stressors=stressors,
            cross_variable_couplings=couplings,
            candidate_interventions=candidates,
            summary_diagnosis=summary_diagnosis
        )

    def _detect_stressors(self, state: EnvironmentalState) -> List[EnvironmentalStressor]:
        stressors: List[EnvironmentalStressor] = []

        # 1. Soil Stressors
        soc = state.soil.organic_carbon_pct
        if soc is not None:
            if soc < 0.5:
                stressors.append(EnvironmentalStressor(
                    category="soil",
                    code="ACUTE_LOW_SOC",
                    severity="high",
                    description=f"Critically low Soil Organic Carbon ({soc}% < 0.5%), impairing biological respiration and cation exchange capacity.",
                    metrics_triggering=["Soil Organic Carbon"]
                ))
            elif soc < 0.75:
                stressors.append(EnvironmentalStressor(
                    category="soil",
                    code="MODERATE_LOW_SOC",
                    severity="moderate",
                    description=f"Sub-optimal Soil Organic Carbon ({soc}% < 0.75%), limiting nutrient cycling efficiency.",
                    metrics_triggering=["Soil Organic Carbon"]
                ))

        if state.soil.ph is not None:
            if state.soil.ph < 5.5:
                stressors.append(EnvironmentalStressor(
                    category="soil",
                    code="SOIL_ACIDITY",
                    severity="moderate",
                    description=f"Soil acidity (pH {state.soil.ph}) restricts microbial activity and phosphorus availability.",
                    metrics_triggering=["Soil pH"]
                ))
            elif state.soil.ph > 8.2:
                stressors.append(EnvironmentalStressor(
                    category="soil",
                    code="SOIL_ALKALINITY",
                    severity="moderate",
                    description=f"Alkaline conditions (pH {state.soil.ph}) induce micronutrient immobilization.",
                    metrics_triggering=["Soil pH"]
                ))

        if state.soil.moisture_pct is not None and state.soil.moisture_pct < 20.0:
            stressors.append(EnvironmentalStressor(
                category="soil",
                code="SOIL_MOISTURE_DEFICIT",
                severity="high",
                description=f"Low volumetric soil moisture ({state.soil.moisture_pct}%) accelerates microbial dormancy.",
                metrics_triggering=["Soil Moisture"]
            ))

        # 2. Climate Stressors
        if state.climate.rainfall == "low" or (state.climate.annual_rainfall_mm is not None and state.climate.annual_rainfall_mm < 600):
            stressors.append(EnvironmentalStressor(
                category="climate",
                code="METEOROLOGICAL_WATER_DEFICIT",
                severity="high",
                description="Arid/semi-arid rainfall deficit, constraining moisture retention and vegetative biomass accumulation.",
                metrics_triggering=["Rainfall", "Water Availability"]
            ))

        if state.climate.drought_frequency in ["frequent", "occasional"]:
            stressors.append(EnvironmentalStressor(
                category="climate",
                code="CHRONIC_DROUGHT_EXPOSURE",
                severity="high" if state.climate.drought_frequency == "frequent" else "moderate",
                description="Periodic drought cycles suppressing native plant survival and microbial resilience.",
                metrics_triggering=["Drought Frequency"]
            ))

        # 3. Land Use Stressors
        if state.land.land_use == "monoculture" or state.land.is_monoculture is True:
            crop_name = state.land.crop or "crop"
            stressors.append(EnvironmentalStressor(
                category="land",
                code="MONOCULTURE_SIMPLIFICATION",
                severity="high",
                description=f"Continuous {crop_name} monoculture eliminates ecological niches, breaks soil food webs, and accelerates nutrient depletion.",
                metrics_triggering=["Land Use", "Crop Diversity"]
            ))

        if state.land.habitat_fragmentation == "high":
            stressors.append(EnvironmentalStressor(
                category="land",
                code="HABITAT_FRAGMENTATION",
                severity="high",
                description="Severe habitat fragmentation disrupts wildlife corridors and dispersal vectors.",
                metrics_triggering=["Habitat Fragmentation"]
            ))

        # 4. Biodiversity Stressors
        if state.biodiversity.species_richness == "low" or state.biodiversity.habitat_diversity == "low":
            stressors.append(EnvironmentalStressor(
                category="biodiversity",
                code="BIODIVERSITY_VULNERABILITY",
                severity="high",
                description="Depressed species richness and structural habitat diversity leave the agroecosystem vulnerable to pest outbreaks and soil degradation.",
                metrics_triggering=["Species Richness", "Habitat Diversity"]
            ))

        if state.biodiversity.pollinator_presence == "rare":
            stressors.append(EnvironmentalStressor(
                category="biodiversity",
                code="POLLINATOR_DEFICIT",
                severity="moderate",
                description="Rare pollinator presence signals floral resource gaps and nesting site depletion.",
                metrics_triggering=["Pollinator Abundance"]
            ))

        # 5. Human Impact Stressors
        if state.human_impact.pesticide_use in ["high", "medium"]:
            stressors.append(EnvironmentalStressor(
                category="human_impact",
                code="CHEMICAL_DISTURBANCE",
                severity="high" if state.human_impact.pesticide_use == "high" else "moderate",
                description="Chemical pesticide pressure depresses beneficial entomofauna and soil mycorrhizal networks.",
                metrics_triggering=["Pesticide Use"]
            ))

        if state.human_impact.water_extraction == "critical":
            stressors.append(EnvironmentalStressor(
                category="human_impact",
                code="AQUIFER_DEPLETION",
                severity="high",
                description="Groundwater extraction exceeding recharge rates, threatening long-term perennial vegetation.",
                metrics_triggering=["Water Extraction"]
            ))

        return stressors

    def _model_couplings(self, state: EnvironmentalState, stressors: List[EnvironmentalStressor]) -> List[CrossVariableCoupling]:
        """
        Explicitly models relationships between multi-metric pairs:
        - Soil health <-> Biodiversity
        - Water availability <-> Species survival
        - Land use <-> Habitat fragmentation
        - Crop diversity <-> Habitat diversity
        - Soil organic carbon <-> Soil biological activity
        - Climate stress <-> Vegetation recovery
        - Human impact <-> Biodiversity decline
        """
        stressor_codes = {s.code for s in stressors}
        couplings: List[CrossVariableCoupling] = []

        # Coupling 1: Low SOC + Low Moisture/Rainfall -> Soil biological activity collapse
        if ("ACUTE_LOW_SOC" in stressor_codes or "MODERATE_LOW_SOC" in stressor_codes) and \
           ("METEOROLOGICAL_WATER_DEFICIT" in stressor_codes or "SOIL_MOISTURE_DEFICIT" in stressor_codes):
            couplings.append(CrossVariableCoupling(
                name="Soil Organic Carbon ↔ Soil Biological Activity Coupling",
                variables_involved=["Soil Organic Carbon", "Rainfall / Soil Moisture", "Microbial Biomass"],
                mechanism="Under moisture-constrained semi-arid conditions, carbon-poor soils lose microbial enzymatic activity, halting aggregate stabilization and exacerbating topsoil desiccation.",
                ecological_risk="Catastrophic decline in microbial diversity and accelerated desertification."
            ))

        # Coupling 2: Monoculture + Low Biodiversity -> Trophic simplification & vulnerability
        if "MONOCULTURE_SIMPLIFICATION" in stressor_codes and "BIODIVERSITY_VULNERABILITY" in stressor_codes:
            couplings.append(CrossVariableCoupling(
                name="Crop Diversity ↔ Habitat Diversity ↔ Biodiversity Coupling",
                variables_involved=["Land Use (Monoculture)", "Species Richness", "Pollinators"],
                mechanism="Monoculture cultivation suppresses spatial and temporal structural heterogeneity, starving pollinators of staggered flowering windows and depriving ground organisms of diverse root exudates.",
                ecological_risk="Loss of natural pest predators and acute reliance on external chemical inputs."
            ))

        # Coupling 3: Water Deficit + Monoculture -> Climate stress ↔ Vegetation recovery failure
        if "METEOROLOGICAL_WATER_DEFICIT" in stressor_codes and "MONOCULTURE_SIMPLIFICATION" in stressor_codes:
            couplings.append(CrossVariableCoupling(
                name="Water Availability ↔ Species Survival & Vegetation Resilience",
                variables_involved=["Rainfall", "Monoculture", "Rooting Depth"],
                mechanism="Monoculture crops exploit only a single uniform soil root zone; under low precipitation, lack of complementary deep-rooted species prevents hydraulic redistribution, causing rapid canopy withering.",
                ecological_risk="Total crop failure during dry spells and complete absence of understory habitat."
            ))

        # Coupling 4: Chemical Disturbance + Biodiversity Vulnerability
        if "CHEMICAL_DISTURBANCE" in stressor_codes and "BIODIVERSITY_VULNERABILITY" in stressor_codes:
            couplings.append(CrossVariableCoupling(
                name="Human Impact ↔ Biodiversity Decline",
                variables_involved=["Pesticide Intensity", "Non-Target Beneficials", "Mycorrhizal Fungi"],
                mechanism="Broad-spectrum inputs decimate predatory insects and disrupt fungal symbiosis required for nutrient extraction in degraded soils.",
                ecological_risk="Secondary pest resurgence and collapse of natural biological regulation."
            ))

        return couplings

    def _generate_and_filter_candidates(
        self,
        state: EnvironmentalState,
        stressors: List[EnvironmentalStressor],
        couplings: List[CrossVariableCoupling],
        constraints: Dict[str, Any]
    ) -> List[CandidateIntervention]:
        stressor_codes = {s.code for s in stressors}
        crop = (state.land.crop or "main crop").lower()
        region = (state.land.region or "semi-arid drylands").lower()
        cannot_change_crop = constraints.get("cannot_change_main_crop", False)

        candidates: List[CandidateIntervention] = []

        # Candidate A: Drought-tolerant Legume Strip Intercropping with Crop Residue Retention
        # Perfectly addresses: Low SOC + Low Rainfall + Monoculture + Crop constraint
        if "ACUTE_LOW_SOC" in stressor_codes or "MONOCULTURE_SIMPLIFICATION" in stressor_codes:
            legume_partner = "chickpea (Cicer arietinum) or pigeonpea (Cajanus cajan)" if "semi-arid" in region or "karnataka" in region else "drought-hardy pulses"
            title = f"Legume Strip-Intercropping ({legume_partner}) with Stubble Retention"
            if cannot_change_crop:
                title = f"In-Situ {legume_partner} Strip Intercropping within Existing {crop.capitalize()} Rows"

            candidates.append(CandidateIntervention(
                id="cand_legume_intercropping",
                title=title,
                primary_category="intercropping",
                description=(
                    f"Integrate paired rows of {legume_partner} alongside primary {crop} without replacing the main cash crop. "
                    f"Retain 30–40% stubble biomass on the surface to curtail evaporation and stimulate microbial detrital food webs."
                ),
                addresses_stressors=["ACUTE_LOW_SOC", "MONOCULTURE_SIMPLIFICATION", "METEOROLOGICAL_WATER_DEFICIT"],
                affected_metrics=[
                    "Soil Organic Carbon",
                    "Soil Moisture Retention",
                    "Soil Microbial Diversity",
                    "Pollinator Abundance",
                    "Habitat Heterogeneity"
                ],
                suitability_score=0.95 if ("METEOROLOGICAL_WATER_DEFICIT" in stressor_codes and cannot_change_crop) else 0.90,
                time_horizon="Medium term",
                rationale_points=[
                    f"Farmer retains {crop.capitalize()} production while introducing nitrogen-fixing legume root exudates.",
                    "Symbiotic Rhizobia enhance soil carbon sequestration and provide alternative floral resources for native bees.",
                    "Crop residue blanket decreases soil surface temperature by 3–6°C and reduces capillary evaporation."
                ],
                rag_search_query=f"semi-arid legume intercropping soil organic carbon moisture microbial diversity {region} FAO"
            ))

        # Candidate B: Field-Margin Multi-Tier Agroforestry & Pollinator Buffer Strips
        # Works even if farmer cannot touch the main cropped area
        if "BIODIVERSITY_VULNERABILITY" in stressor_codes or "METEOROLOGICAL_WATER_DEFICIT" in stressor_codes:
            trees = "Acacia nilotica, Melia dubia, and Pongamia pinnata" if "karnataka" in region or "semi-arid" in region else "deep-rooted drought-resilient native woody perennials"
            candidates.append(CandidateIntervention(
                id="cand_field_margin_agroforestry",
                title="Field-Border Multi-Tier Agroforestry & Native Flowering Hedgerows",
                primary_category="agroforestry",
                description=(
                    f"Establish boundary shelterbelts using indigenous drought-hardy species ({trees}) "
                    f"underplanted with flowering perennial shrubs along field perimeters."
                ),
                addresses_stressors=["BIODIVERSITY_VULNERABILITY", "POLLINATOR_DEFICIT", "METEOROLOGICAL_WATER_DEFICIT"],
                affected_metrics=[
                    "Habitat Diversity",
                    "Pollinator Presence",
                    "Wind Erosion Reduction",
                    "Deep Soil Carbon Stock"
                ],
                suitability_score=0.88,
                time_horizon="Long term",
                rationale_points=[
                    "Creates continuous vegetative windbreaks that slash windward evapotranspiration by 15–20%.",
                    "Establishes permanent nesting microhabitats for pollinators and avian predators of crop pests.",
                    "Root architecture accesses subsoil water tables without competing with shallow crop roots."
                ],
                rag_search_query="boundary agroforestry shelterbelts semi-arid pollinator habitat microclimate FAO ICRAF"
            ))

        # Candidate C: Biochar-Compost Enriched Micro-Dosing (Targeted Soil Rehabilitation)
        if ("ACUTE_LOW_SOC" in stressor_codes or "MODERATE_LOW_SOC" in stressor_codes) and \
           ("SOIL_MOISTURE_DEFICIT" in stressor_codes or "METEOROLOGICAL_WATER_DEFICIT" in stressor_codes or "ACUTE_LOW_SOC" in stressor_codes):
            candidates.append(CandidateIntervention(
                id="cand_biochar_compost",
                title="In-Furrow Biochar-Compost Mineral Inoculation",
                primary_category="soil_rehabilitation",
                description=(
                    "Apply locally pyrolyzed crop residue biochar co-composted with farmyard manure directly into seed furrows "
                    "at planting, concentrating organic matrices where roots germinate."
                ),
                addresses_stressors=["ACUTE_LOW_SOC", "METEOROLOGICAL_WATER_DEFICIT"],
                affected_metrics=[
                    "Soil Organic Carbon",
                    "Plant-Available Water Capacity",
                    "Mycorrhizal Fungal Inoculation"
                ],
                suitability_score=0.85,
                time_horizon="Short term",
                rationale_points=[
                    "Biochar provides recalcitrant porous carbon frameworks that hold capillary water in drought conditions.",
                    "Micro-dosing avoids prohibitive volume requirements of broadcast organic amendments in semi-arid zones."
                ],
                rag_search_query="biochar compost micro-dosing semi-arid soil moisture retention organic carbon IPCC"
            ))

        # Candidate D: Conservation Zero-Tillage & In-Situ Surface Mulching
        if "MONOCULTURE_SIMPLIFICATION" in stressor_codes or "ACUTE_LOW_SOC" in stressor_codes or "METEOROLOGICAL_WATER_DEFICIT" in stressor_codes:
            candidates.append(CandidateIntervention(
                id="cand_conservation_tillage",
                title="Conservation Zero-Tillage with Standing Crop Residue Mulching",
                primary_category="conservation_tillage",
                description=(
                    f"Transition from conventional tillage to direct zero-till seeding into standing crop stubbles. "
                    f"Maintain a protective 2–3 ton/ha biological mulch layer on topsoil year-round."
                ),
                addresses_stressors=["ACUTE_LOW_SOC", "METEOROLOGICAL_WATER_DEFICIT", "MONOCULTURE_SIMPLIFICATION"],
                affected_metrics=[
                    "Soil Organic Carbon",
                    "Soil Bulk Density",
                    "Soil Evaporation Suppression",
                    "Macro-aggregate Stability"
                ],
                suitability_score=0.87,
                time_horizon="Short term",
                rationale_points=[
                    "Zero-tillage eliminates mechanical disturbance that rapidly oxidizes labile organic carbon in semi-arid heat.",
                    "Standing surface residue reflects solar radiation, moderating topsoil temperatures by 4–8°C.",
                    "Significantly improves water infiltration rates while protecting fragile surface aggregates from crusting."
                ],
                rag_search_query="conservation agriculture zero tillage residue retention soil carbon semi-arid FAO"
            ))

        # Rank candidates by suitability score
        candidates.sort(key=lambda c: c.suitability_score, reverse=True)
        return candidates

    def _generate_diagnosis_text(
        self,
        state: EnvironmentalState,
        stressors: List[EnvironmentalStressor],
        couplings: List[CrossVariableCoupling]
    ) -> str:
        if not stressors:
            return "Environmental metrics indicate a stable baseline with no critical degradation thresholds breached."

        stressor_names = [s.description for s in stressors[:3]]
        couplings_summary = " Additionally, " + " ".join([c.mechanism for c in couplings[:2]]) if couplings else ""
        return f"Identified {len(stressors)} core environmental stressor(s): " + "; ".join(stressor_names) + "." + couplings_summary

reasoning_engine = EnvironmentalReasoningEngine()
