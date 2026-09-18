from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.schemas.recommendation import RecommendationOutput
from backend.app.schemas.retrieval import RetrievalTrace

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., description="Natural language input or question from the user")
    structured_state: Optional[Dict[str, Any]] = Field(None, description="Optional structured JSON input")
    land_profile_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    extracted_state: EnvironmentalState
    is_information_complete: bool
    clarifying_questions: List[str] = Field(default_factory=list)
    recommendations: List[RecommendationOutput] = Field(default_factory=list)
    retrieval_trace: Optional[RetrievalTrace] = None
    multi_metric_stressors: List[str] = Field(default_factory=list)
    detected_interactions: List[str] = Field(default_factory=list)
