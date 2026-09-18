import pytest
from backend.app.services.rag_service import ScientificRAGService, rag_service
from backend.app.services.claim_safety import ClaimSafetyEngine, claim_safety_engine

@pytest.fixture
def rag():
    return rag_service

@pytest.fixture
def safety():
    return claim_safety_engine

def test_rag_semantic_search_and_metadata_filtering(rag):
    """
    Verifies that the RAG retrieval pipeline retrieves real institutional scientific evidence
    and respects region and metric filters.
    """
    query = "semi-arid legume intercropping soil organic carbon moisture"
    trace = rag.search(
        query=query,
        target_metrics=["soil_organic_carbon", "soil_moisture", "nitrogen_fixation"],
        region_filter="Semi-arid Karnataka",
        top_k=3
    )

    assert trace.total_documents_scanned >= 5
    assert len(trace.sources_retrieved) == 3
    assert trace.top_relevance_score >= 0.80

    top_doc = trace.sources_retrieved[0]
    # Top documents should be institutional research from FAO, ICRISAT, or IPCC
    assert top_doc.organization in [
        "Food and Agriculture Organization of the United Nations (FAO)",
        "International Crops Research Institute for the Semi-Arid Tropics (ICRISAT)",
        "World Agroforestry (ICRAF) & CIFOR",
        "Intergovernmental Panel on Climate Change (IPCC)"
    ]
    assert len(top_doc.evidence_text) > 50
    assert len(top_doc.quantified_claims) > 0
    assert "Karnataka" in top_doc.region or "Drylands" in top_doc.region or "Semi-arid" in top_doc.region

def test_rag_retrieval_trace_structure(rag):
    """
    Verifies that RAG returns a complete, transparent retrieval trace with
    relevance scores, rationale, and metadata.
    """
    query = "boundary shelterbelts windbreak pollinator habitat"
    trace = rag.search(query=query, target_metrics=["pollinator_abundance"], top_k=2)

    assert trace.query == query
    assert len(trace.sources_retrieved) == 2
    for doc in trace.sources_retrieved:
        assert doc.relevance_score > 0.65
        assert doc.match_rationale != ""
        assert doc.year >= 2019
        assert doc.document_type != ""

def test_claim_safety_verifies_grounded_claims(rag, safety):
    """
    Verifies that the Claim Safety Engine confirms substantiated claims
    with real citations from FAO.
    """
    trace = rag.search(
        query="recarbonizing soils residue retention organic carbon",
        target_metrics=["soil_organic_carbon"],
        top_k=2
    )

    evidence_chunks = [d.model_dump() for d in trace.sources_retrieved]

    grounded_claim_text = (
        "Implementing conservation agriculture with residue retention increases topsoil "
        "organic carbon by 0.15% to 0.35% over 3 to 5 years."
    )

    audit = safety.audit_intervention_claim(
        claim_text=grounded_claim_text,
        retrieved_evidence_chunks=evidence_chunks
    )

    assert audit.grounding_status == "FULLY_GROUNDED"
    assert len(audit.verified_citations) > 0
    assert any("FAO" in c for c in audit.verified_citations)
    assert len(audit.quantified_claims) > 0

def test_claim_safety_mitigates_hallucinated_statistics(rag, safety):
    """
    Verifies that invented numbers without backing in evidence are flagged,
    audited, and mitigated rather than blindly repeated.
    """
    trace = rag.search(
        query="legume intercropping nitrogen fixation",
        target_metrics=["nitrogen_fixation"],
        top_k=2
    )
    evidence_chunks = [d.model_dump() for d in trace.sources_retrieved]

    # 890 kg N/ha is an absurd hallucination not present in scientific literature
    hallucinated_claim_text = "This method fixes 890 kg N/ha instantly in one week."

    audit = safety.audit_intervention_claim(
        claim_text=hallucinated_claim_text,
        retrieved_evidence_chunks=evidence_chunks,
        strict_mode=True
    )

    assert audit.grounding_status == "QUALIFIED_CONSERVATIVE"
    assert len(audit.safety_notes) > 0
    assert "890" in audit.safety_notes[0]
    assert "890" not in audit.audited_text

def test_claim_safety_rejects_empty_evidence(safety):
    """
    Verifies that if no scientific evidence supports an intervention,
    the claim is rejected.
    """
    audit = safety.audit_intervention_claim(
        claim_text="Applying chemical X cures drought.",
        retrieved_evidence_chunks=[]
    )

    assert audit.grounding_status == "UNGROUNDED_REJECTED"
    assert "No verified scientific evidence" in audit.audited_text

def test_rag_chromadb_vector_retrieval_and_trace(rag):
    """
    Verifies that ChromaDB semantic vector retrieval is genuinely active,
    computes vector distances, and returns full retrieval traces.
    """
    trace = rag.search(
        query="legume strip intercropping Vertisols nitrogen phosphorus",
        target_metrics=["nitrogen_fixation", "soil_organic_carbon"],
        region_filter="Semi-arid Karnataka",
        top_k=3
    )

    assert "ChromaDB" in trace.vector_backend
    assert "ChromaDB Semantic Vector Retrieval" in trace.retrieval_mode
    assert len(trace.vector_retrieved_ids) > 0
    assert trace.total_documents_scanned == 6

    for src in trace.sources_retrieved:
        assert src.vector_distance is not None
        assert 0.0 <= src.vector_distance <= 2.0
        assert src.semantic_similarity is not None
        assert 0.0 <= src.semantic_similarity <= 1.0
        assert src.reranking_score is not None

def test_scientific_corpus_doi_integrity(rag):
    """
    Verifies that every document in the scientific corpus has an authentic,
    verified DOI or official institutional publication URL.
    No synthetic or guessed URLs (e.g. 10.fao.org) are permitted.
    """
    for doc in rag.documents:
        doi_or_url = doc.get("doi_or_url")
        assert doi_or_url is not None and len(doi_or_url) > 0
        # Must not be a placeholder or synthetic pattern
        assert "10.fao.org" not in doi_or_url
        assert "10.ipcc.org" not in doi_or_url
        assert "10.icraf.org" not in doi_or_url
        assert "10.icrisat.org" not in doi_or_url
        # Must start with https:// or http://
        assert doi_or_url.startswith("http://") or doi_or_url.startswith("https://")
        # Must either be a valid registered DOI or official institutional portal
        is_doi = "doi.org/10.4060/" in doi_or_url or "doi.org/10.1017/" in doi_or_url
        is_inst_url = "worldagroforestry.org" in doi_or_url or "icrisat.org" in doi_or_url or "sciencedirect.com" in doi_or_url or "fao.org" in doi_or_url or "ipcc.ch" in doi_or_url
        assert is_doi or is_inst_url

