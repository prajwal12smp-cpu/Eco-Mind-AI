from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field

class RetrievedEvidence(BaseModel):
    source_title: str
    organization: str
    year: int
    document_type: str = "report"
    relevance_score: float
    evidence_text: str
    reported_change: Optional[str] = None  # e.g., "15–25% over 2–3 years (FAO studies)"
    doi_or_url: Optional[str] = None
    vector_distance: Optional[float] = None
    semantic_similarity: Optional[float] = None
    reranking_score: Optional[float] = None
    match_rationale: Optional[str] = None

class RetrievalTrace(BaseModel):
    query: str
    retrieval_mode: str = "ChromaDB Semantic Vector Retrieval + Metadata Guided Reranking"
    vector_backend: str = "ChromaDB (chromadb v1.5.9)"
    vector_retrieved_ids: List[str] = Field(default_factory=list)
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    sources: List[RetrievedEvidence] = Field(default_factory=list)
    total_documents_scanned: int = 6
    top_score: Optional[float] = None

