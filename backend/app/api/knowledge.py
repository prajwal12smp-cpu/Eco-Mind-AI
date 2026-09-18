from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, status

from backend.app.schemas.retrieval import RetrievalTrace, RetrievedEvidence
from backend.app.services.rag_service import rag_service

router = APIRouter(prefix="/knowledge", tags=["Scientific Knowledge Base & RAG Retrieval"])

@router.get("/search", response_model=RetrievalTrace)
def search_knowledge_base(
    query: str = Query(..., description="Ecological question or intervention topic"),
    target_metric: Optional[str] = Query(None, description="Optional target metric filter (e.g. 'Soil organic carbon')"),
    region: Optional[str] = Query(None, description="Optional region filter (e.g. 'semi-arid')"),
    top_k: int = Query(3, ge=1, le=10)
):
    """
    Direct endpoint to perform transparent semantic search across institutional documents
    (FAO, IPCC, ICRAF, ICRISAT). Returns match scores, extracted snippets, and verified citations.
    """
    target_metrics = [target_metric] if target_metric else None
    trace = rag_service.search(
        query=query,
        target_metrics=target_metrics,
        region_filter=region,
        top_k=top_k
    )

    sources = [
        RetrievedEvidence(
            source_title=s.title,
            organization=s.organization,
            year=s.year,
            document_type=s.document_type,
            relevance_score=s.relevance_score,
            evidence_text=s.evidence_text,
            reported_change=s.quantified_claims[0].get("change_range") if s.quantified_claims else None,
            doi_or_url=s.doi_or_url,
            vector_distance=s.vector_distance,
            semantic_similarity=s.semantic_similarity,
            reranking_score=s.reranking_score,
            match_rationale=s.match_rationale
        )
        for s in trace.sources_retrieved
    ]

    return RetrievalTrace(
        query=trace.query,
        retrieval_mode=trace.retrieval_mode,
        vector_backend=trace.vector_backend,
        vector_retrieved_ids=trace.vector_retrieved_ids,
        filters_applied=trace.filters_applied,
        sources=sources,
        total_documents_scanned=trace.total_documents_scanned,
        top_score=trace.top_relevance_score
    )

@router.get("/documents")
def list_indexed_documents():
    """
    Returns inventory of all authoritative publications indexed in the EcoMind knowledge base.
    """
    corpus = rag_service.documents
    docs = []
    for item in corpus:
        docs.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "organization": item.get("organization"),
            "year": item.get("year"),
            "document_type": item.get("document_type"),
            "region": item.get("region"),
            "metrics": item.get("metrics", []),
            "target_metrics": item.get("metrics", []),
            "doi_or_url": item.get("doi_or_url") or item.get("official_url"),
            "quantified_claims_count": len(item.get("quantified_claims", []))
        })
    return {"total_documents": len(docs), "documents": docs}
