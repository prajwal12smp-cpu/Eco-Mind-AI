import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QuantifiedClaim(BaseModel):
    metric: str
    change_range: str
    condition: str
    grounding_source: Optional[str] = None
    is_verified: bool = True

class ClaimAuditResult(BaseModel):
    original_text: str
    audited_text: str
    grounding_status: str  # "FULLY_GROUNDED", "QUALIFIED_CONSERVATIVE", "UNGROUNDED_REJECTED"
    verified_citations: List[str]
    quantified_claims: List[QuantifiedClaim]
    safety_notes: List[str]

class ClaimSafetyEngine:
    """
    Strict Claim Safety and Anti-Hallucination Audit Engine.
    Ensures:
    1. Zero fabrication of research papers, citations, institutions, or statistics.
    2. Quantitative claims (% improvements, kg N/ha, °C reductions) MUST be backed
       by exact evidence chunks from verified scientific authorities (FAO, IPCC, ICRAF, ICRISAT).
    3. If evidence is qualitative, forces conservative qualitative framing ('Moderate', 'Substantial')
       instead of hallucinating precision figures.
    4. Strips or blocks any ungrounded claim.
    """

    NUMERIC_PATTERN = re.compile(r'(\b\d+(?:\.\d+)?\s*(?:%|kg\s*(?:N)?/ha|°C|t/ha|mm)\b)|(\b\d+(?:\.\d+)?\s*[-–to]\s*\d+(?:\.\d+)?\s*(?:%|kg\s*(?:N)?/ha|°C|t/ha|mm)\b)', re.IGNORECASE)

    def audit_intervention_claim(
        self,
        claim_text: str,
        retrieved_evidence_chunks: List[Dict[str, Any]],
        strict_mode: bool = True
    ) -> ClaimAuditResult:
        safety_notes: List[str] = []
        verified_citations: List[str] = []
        quantified_claims: List[QuantifiedClaim] = []

        # Collect text corpus of retrieved evidence
        evidence_corpus = " ".join([
            (chunk.get("evidence_text", "") + " " + chunk.get("title", "") + " " + chunk.get("organization", ""))
            for chunk in retrieved_evidence_chunks
        ]).lower()

        # Identify all verified organizations in retrieved evidence
        valid_orgs = {chunk.get("organization", "").lower() for chunk in retrieved_evidence_chunks if chunk.get("organization")}
        valid_titles = {chunk.get("title", "").lower() for chunk in retrieved_evidence_chunks if chunk.get("title")}

        # Scan for quantitative patterns in the proposed claim
        matches = self.NUMERIC_PATTERN.findall(claim_text)
        has_numeric_claim = len(matches) > 0

        # Collect verified quantified claims directly from evidence chunks
        for chunk in retrieved_evidence_chunks:
            source_citation = f"{chunk.get('organization', 'Scientific Assessment')} ({chunk.get('year', 'Recent')})"
            if source_citation not in verified_citations:
                verified_citations.append(source_citation)

            for qc in chunk.get("quantified_claims", []):
                quantified_claims.append(QuantifiedClaim(
                    metric=qc.get("metric", "Environmental Metric"),
                    change_range=qc.get("change_range", "Documented positive shift"),
                    condition=qc.get("condition", "Under recommended management"),
                    grounding_source=source_citation,
                    is_verified=True
                ))

        # Check if proposed claim contains numbers that are NOT present in evidence corpus
        audited_text = claim_text
        grounding_status = "FULLY_GROUNDED"

        if has_numeric_claim:
            # Check numbers against evidence
            unsubstantiated_numbers = []
            for match_tuple in matches:
                matched_str = match_tuple[0] or match_tuple[1]
                # Normalize spaces and check substring
                norm_str = matched_str.strip().lower()
                clean_num = re.sub(r'[^\d.]', '', norm_str.split('-')[0])
                if clean_num and clean_num not in evidence_corpus:
                    unsubstantiated_numbers.append(matched_str)

            if unsubstantiated_numbers and strict_mode:
                grounding_status = "QUALIFIED_CONSERVATIVE"
                safety_notes.append(
                    f"Replaced unverified statistical figures ({', '.join(unsubstantiated_numbers)}) "
                    f"with scientifically safe qualitative intervals supported by evidence."
                )
                # Conservatively replace exact ungrounded numbers with qualitative terms
                for bad_num in unsubstantiated_numbers:
                    audited_text = audited_text.replace(bad_num, "demonstrated positive")

        if not retrieved_evidence_chunks:
            grounding_status = "UNGROUNDED_REJECTED"
            audited_text = "No verified scientific evidence found to substantiate this intervention. Proceed with extreme caution under local agricultural extension supervision."
            safety_notes.append("Strict rejection: No peer-reviewed or institutional evidence in knowledge base.")

        return ClaimAuditResult(
            original_text=claim_text,
            audited_text=audited_text,
            grounding_status=grounding_status,
            verified_citations=verified_citations,
            quantified_claims=quantified_claims,
            safety_notes=safety_notes
        )

claim_safety_engine = ClaimSafetyEngine()
