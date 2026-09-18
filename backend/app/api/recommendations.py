from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.recommendation import Recommendation
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.schemas.recommendation import RecommendationOutput
from backend.app.schemas.retrieval import RetrievedEvidence
from backend.app.services.reasoning_engine import reasoning_engine
from backend.app.services.rag_service import rag_service
from backend.app.services.claim_safety import claim_safety_engine

router = APIRouter(prefix="/recommendations", tags=["Ecological Recommendations & Audits"])

@router.post("/analyze", response_model=List[RecommendationOutput])
def analyze_environmental_state(state: EnvironmentalState):
    """
    Direct multi-metric analysis endpoint:
    Performs deterministic constraint reasoning, RAG retrieval across FAO/IPCC/ICRAF/ICRISAT corpus,
    and claim safety auditing on arbitrary environmental metric inputs.
    """
    analysis = reasoning_engine.analyze(state)
    results: List[RecommendationOutput] = []

    for cand in analysis.candidate_interventions:
        rag_trace = rag_service.search(
            query=cand.rag_search_query,
            target_metrics=cand.affected_metrics,
            region_filter=state.land.region,
            top_k=2
        )

        evidence_items: List[RetrievedEvidence] = []
        for src in rag_trace.sources_retrieved:
            rep_change = src.quantified_claims[0].get("change_range") if src.quantified_claims else None
            evidence_items.append(RetrievedEvidence(
                source_title=src.title,
                organization=src.organization,
                year=src.year,
                document_type=src.document_type,
                relevance_score=src.relevance_score,
                evidence_text=src.evidence_text,
                reported_change=rep_change,
                doi_or_url=src.doi_or_url
            ))

        evidence_dicts = [s.model_dump() for s in rag_trace.sources_retrieved]
        audit_res = claim_safety_engine.audit_intervention_claim(
            claim_text=cand.description,
            retrieved_evidence_chunks=evidence_dicts,
            strict_mode=True
        )

        why_steps = [
            f"Addressed active stressors: {', '.join(cand.addresses_stressors)}",
            f"Multi-metric co-benefits across: {', '.join(cand.affected_metrics)}"
        ]
        if audit_res.verified_citations:
            why_steps.append(f"Grounded by literature: {', '.join(audit_res.verified_citations)}")

        results.append(RecommendationOutput(
            id=cand.id,
            title=cand.title,
            directive=audit_res.audited_text,
            scientific_rationale=" ".join(cand.rationale_points),
            environmental_metrics_affected=cand.affected_metrics,
            time_horizon=cand.time_horizon,
            confidence="High" if rag_trace.top_relevance_score >= 0.80 else "Medium",
            evidence=evidence_items,
            why_this_recommendation=why_steps,
            claim_type="evidence_supported_interval" if audit_res.grounding_status == "FULLY_GROUNDED" else "qualitative_estimate",
            reported_change=evidence_items[0].reported_change if evidence_items else None
        ))

    return results

@router.get("/{recommendation_id}")
def get_recommendation_details(recommendation_id: str, db: Session = Depends(get_db)):
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    sources = [
        {
            "id": s.id,
            "title": s.title,
            "organization": s.organization,
            "year": s.year,
            "document_type": s.document_type,
            "relevance_score": s.relevance_score,
            "evidence_snippet": s.evidence_snippet,
            "doi_or_url": s.doi_or_url
        }
        for s in rec.sources
    ]

    return {
        "id": rec.id,
        "land_profile_id": rec.land_profile_id,
        "title": rec.title,
        "directive": rec.directive,
        "scientific_rationale": rec.scientific_rationale,
        "impacted_metrics": rec.impacted_metrics,
        "time_horizon": rec.time_horizon,
        "confidence_level": rec.confidence_level,
        "reasoning_trace": rec.reasoning_trace,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
        "sources": sources
    }
