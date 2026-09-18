import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.land_profile import LandProfile
from backend.app.models.metrics import SoilMetric, ClimateMetric, BiodiversityMetric, HumanImpactMetric
from backend.app.models.recommendation import Recommendation
from backend.app.schemas.land_profile import LandProfileCreate, LandProfileResponse, DashboardData
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState
)
from backend.app.schemas.recommendation import RecommendationOutput
from backend.app.schemas.retrieval import RetrievedEvidence
from backend.app.services.reasoning_engine import reasoning_engine

router = APIRouter(prefix="/land-profiles", tags=["Land Profiles & Farm Baseline"])

def _build_current_state(profile: LandProfile) -> EnvironmentalState:
    soil = SoilState()
    if profile.soil_metrics:
        latest_soil = profile.soil_metrics[-1]
        soil = SoilState(
            organic_carbon_pct=latest_soil.organic_carbon_pct,
            ph=latest_soil.ph,
            moisture_pct=latest_soil.moisture_pct,
            nitrogen_ppm=latest_soil.nitrogen_ppm,
            texture=latest_soil.texture
        )

    climate = ClimateState()
    if profile.climate_metrics:
        latest_climate = profile.climate_metrics[-1]
        climate = ClimateState(
            rainfall=latest_climate.rainfall_category,
            annual_rainfall_mm=latest_climate.annual_rainfall_mm,
            temperature_celsius=latest_climate.avg_temperature_celsius,
            drought_frequency=latest_climate.drought_frequency,
            water_availability=latest_climate.water_availability
        )

    biodiversity = BiodiversityState()
    if profile.biodiversity_metrics:
        latest_bio = profile.biodiversity_metrics[-1]
        biodiversity = BiodiversityState(
            species_richness=latest_bio.species_richness_index,
            habitat_diversity=latest_bio.habitat_diversity_index,
            pollinator_presence=latest_bio.pollinator_presence,
            native_species_ratio=latest_bio.native_plant_ratio
        )

    human_impact = HumanImpactState()
    if profile.human_impact_metrics:
        latest_human = profile.human_impact_metrics[-1]
        human_impact = HumanImpactState(
            pesticide_use=latest_human.pesticide_intensity,
            water_extraction=latest_human.water_extraction_rate,
            deforestation_proximity=latest_human.deforestation_proximity
        )

    land = LandState(
        region=profile.region,
        crop=profile.primary_crop,
        land_use=profile.farming_system,
        area_hectares=profile.area_hectares,
        is_monoculture=(profile.farming_system.lower() == "monoculture") if profile.farming_system else None
    )

    return EnvironmentalState(
        soil=soil,
        land=land,
        biodiversity=biodiversity,
        climate=climate,
        human_impact=human_impact
    )

@router.post("", response_model=LandProfileResponse, status_code=status.HTTP_201_CREATED)
def create_land_profile(payload: LandProfileCreate, db: Session = Depends(get_db)):
    profile = LandProfile(
        id=str(uuid.uuid4()),
        name=payload.name,
        region=payload.region,
        latitude=payload.latitude,
        longitude=payload.longitude,
        area_hectares=payload.area_hectares,
        primary_crop=payload.primary_crop,
        farming_system=payload.farming_system
    )
    db.add(profile)
    db.flush()

    if payload.initial_state:
        st = payload.initial_state
        if st.soil.model_dump(exclude_none=True):
            db.add(SoilMetric(
                land_profile_id=profile.id,
                organic_carbon_pct=st.soil.organic_carbon_pct,
                ph=st.soil.ph,
                moisture_pct=st.soil.moisture_pct,
                nitrogen_ppm=st.soil.nitrogen_ppm,
                texture=st.soil.texture
            ))
        if st.climate.model_dump(exclude_none=True):
            db.add(ClimateMetric(
                land_profile_id=profile.id,
                rainfall_category=st.climate.rainfall,
                annual_rainfall_mm=st.climate.annual_rainfall_mm,
                avg_temperature_celsius=st.climate.temperature_celsius,
                drought_frequency=st.climate.drought_frequency,
                water_availability=st.climate.water_availability
            ))
        if st.biodiversity.model_dump(exclude_none=True):
            db.add(BiodiversityMetric(
                land_profile_id=profile.id,
                species_richness_index=st.biodiversity.species_richness,
                habitat_diversity_index=st.biodiversity.habitat_diversity,
                pollinator_presence=st.biodiversity.pollinator_presence,
                native_plant_ratio=st.biodiversity.native_species_ratio
            ))
        if st.human_impact.model_dump(exclude_none=True):
            db.add(HumanImpactMetric(
                land_profile_id=profile.id,
                pesticide_intensity=st.human_impact.pesticide_use,
                water_extraction_rate=st.human_impact.water_extraction,
                deforestation_proximity=st.human_impact.deforestation_proximity
            ))

    db.commit()
    db.refresh(profile)

    current_state = _build_current_state(profile)
    return LandProfileResponse(
        id=profile.id,
        name=profile.name,
        region=profile.region,
        latitude=profile.latitude,
        longitude=profile.longitude,
        area_hectares=profile.area_hectares,
        primary_crop=profile.primary_crop,
        farming_system=profile.farming_system,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        current_state=current_state
    )

@router.get("", response_model=List[LandProfileResponse])
def list_land_profiles(db: Session = Depends(get_db)):
    profiles = db.query(LandProfile).order_by(LandProfile.created_at.desc()).all()
    results = []
    for p in profiles:
        st = _build_current_state(p)
        results.append(LandProfileResponse(
            id=p.id,
            name=p.name,
            region=p.region,
            latitude=p.latitude,
            longitude=p.longitude,
            area_hectares=p.area_hectares,
            primary_crop=p.primary_crop,
            farming_system=p.farming_system,
            created_at=p.created_at,
            updated_at=p.updated_at,
            current_state=st
        ))
    return results

@router.get("/{profile_id}", response_model=LandProfileResponse)
def get_land_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(LandProfile).filter(LandProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land profile not found")
    
    st = _build_current_state(profile)
    return LandProfileResponse(
        id=profile.id,
        name=profile.name,
        region=profile.region,
        latitude=profile.latitude,
        longitude=profile.longitude,
        area_hectares=profile.area_hectares,
        primary_crop=profile.primary_crop,
        farming_system=profile.farming_system,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        current_state=st
    )

@router.get("/{profile_id}/dashboard", response_model=DashboardData)
def get_profile_dashboard(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(LandProfile).filter(LandProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land profile not found")

    state = _build_current_state(profile)
    analysis = reasoning_engine.analyze(state)

    recent_recs: List[RecommendationOutput] = []
    for r in profile.recommendations[-5:]:
        evidence_list = [
            RetrievedEvidence(
                source_title=s.title,
                organization=s.organization,
                year=s.year,
                document_type=s.document_type,
                relevance_score=s.relevance_score,
                evidence_text=s.evidence_snippet,
                doi_or_url=s.doi_or_url
            )
            for s in r.sources
        ]
        recent_recs.append(RecommendationOutput(
            id=r.id,
            title=r.title,
            directive=r.directive,
            scientific_rationale=r.scientific_rationale,
            environmental_metrics_affected=r.impacted_metrics,
            time_horizon=r.time_horizon,
            confidence=r.confidence_level,
            evidence=evidence_list,
            why_this_recommendation=r.reasoning_trace or []
        ))

    return DashboardData(
        land_id=profile.id,
        name=profile.name,
        region=profile.region,
        primary_crop=profile.primary_crop,
        farming_system=profile.farming_system,
        metrics=state,
        active_stressors=[s.description for s in analysis.stressors],
        cross_variable_couplings=[f"{c.name}: {c.mechanism}" for c in analysis.cross_variable_couplings],
        recent_recommendations=recent_recs
    )
