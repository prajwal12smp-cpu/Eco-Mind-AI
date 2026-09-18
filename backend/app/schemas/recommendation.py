from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from backend.app.schemas.retrieval import RetrievedEvidence

class RecommendationOutput(BaseModel):
    id: Optional[str] = None
    title: str
    directive: str = Field(..., description="Actionable intervention statement: what should the user do?")
    scientific_rationale: str = Field(..., description="Why it works: ecological and biological mechanisms")
    environmental_metrics_affected: List[str] = Field(
        ..., description="List of environmental metrics affected, e.g. Soil organic carbon, Habitat diversity"
    )
    time_horizon: Literal["Short term", "Medium term", "Long term"]
    confidence: Literal["High", "Medium", "Low"]
    evidence: List[RetrievedEvidence] = Field(default_factory=list)
    why_this_recommendation: List[str] = Field(
        default_factory=list,
        description="Explainable step-by-step reasoning trace without exposing hidden internal prompts"
    )
    claim_type: Literal["evidence_supported_interval", "qualitative_estimate"] = "qualitative_estimate"
    reported_change: Optional[str] = None
