from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.schemas.recommendation import RecommendationOutput

class LandProfileCreate(BaseModel):
    name: str = Field(default="My Plot", description="Identifier name for the land plot")
    region: str = Field(..., description="Agro-climatic region (e.g. semi-arid Karnataka)")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_hectares: Optional[float] = None
    primary_crop: Optional[str] = None
    farming_system: Optional[str] = None
    initial_state: Optional[EnvironmentalState] = None

class LandProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    region: str
    latitude: Optional[float]
    longitude: Optional[float]
    area_hectares: Optional[float]
    primary_crop: Optional[str]
    farming_system: Optional[str]
    created_at: datetime
    updated_at: datetime
    current_state: EnvironmentalState

class DashboardData(BaseModel):
    land_id: str
    name: str
    region: str
    primary_crop: Optional[str]
    farming_system: Optional[str]
    metrics: EnvironmentalState
    active_stressors: List[str]
    cross_variable_couplings: List[str]
    recent_recommendations: List[RecommendationOutput]
