import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.app.models.conversation import Conversation, ConversationMessage
from backend.app.models.land_profile import LandProfile
from backend.app.models.metrics import SoilMetric, ClimateMetric, BiodiversityMetric, HumanImpactMetric
from backend.app.models.recommendation import Recommendation, Source
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState
)
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.schemas.recommendation import RecommendationOutput
from backend.app.schemas.retrieval import RetrievedEvidence, RetrievalTrace
from backend.app.services.state_extractor import state_extractor
from backend.app.services.clarifying_engine import clarifying_engine
from backend.app.services.reasoning_engine import reasoning_engine
from backend.app.services.rag_service import rag_service
from backend.app.services.claim_safety import claim_safety_engine

class EcoMindOrchestrator:
    """
    Central Orchestration Pipeline for EcoMind AI:
    1. Multi-Turn Conversational Memory & State Extraction
    2. Dynamic Clarifying Question Filtering (High-entropy variables)
    3. Deterministic Multi-Metric Ecological Reasoning
    4. Scientific RAG Retrieval & Citation Association (FAO, IPCC, ICRAF, ICRISAT)
    5. Strict Anti-Hallucination Claim Safety Audit
    6. Relational Persistence of Turns, Metrics & Grounded Directives
    """

    def handle_chat_turn(self, db: Session, request: ChatRequest) -> ChatResponse:
        # 1. Resolve or Create Conversation
        conv_id = request.conversation_id or str(uuid.uuid4())
        conversation = db.query(Conversation).filter(Conversation.id == conv_id).first()

        if not conversation:
            conversation = Conversation(
                id=conv_id,
                land_profile_id=request.land_profile_id
            )
            db.add(conversation)
            db.flush()
        elif request.land_profile_id and not conversation.land_profile_id:
            conversation.land_profile_id = request.land_profile_id
            db.flush()

        # 2. Reconstruct Multi-Turn Environmental State Memory
        previous_state = self._reconstruct_state_from_history(conversation)

        # 3. Detect User Constraints (e.g. "cannot change main crop")
        user_constraints: Dict[str, Any] = {}
        lower_msg = request.message.lower()
        if any(term in lower_msg for term in ["cannot change", "can't change", "won't change", "not change", "keep my"]) and ("crop" in lower_msg or "wheat" in lower_msg):
            user_constraints["cannot_change_main_crop"] = True

        # 4. Extract Current Turn State
        current_state = state_extractor.extract_state(
            user_text=request.message,
            structured_state=request.structured_state,
            previous_state=previous_state
        )

        # 5. Evaluate Information Completeness
        is_complete, clarifying_questions = clarifying_engine.evaluate_completeness(current_state)

        # If incomplete, respond with clarifying questions and do not output ungrounded guesses
        if not is_complete:
            assistant_content = (
                "I have registered your environmental indicators. However, to formulate scientifically sound, "
                "multi-metric recommendations without broad generalizations, I need a few critical missing parameters:\n\n"
                + "\n".join([f"• {q}" for q in clarifying_questions])
            )

            # Persist turns
            user_msg = ConversationMessage(
                conversation_id=conversation.id,
                role="user",
                content=request.message,
                extracted_state=current_state.model_dump()
            )
            asst_msg = ConversationMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=assistant_content,
                extracted_state=current_state.model_dump(),
                clarifications_requested=clarifying_questions
            )
            db.add(user_msg)
            db.add(asst_msg)
            db.commit()

            return ChatResponse(
                conversation_id=conversation.id,
                message=assistant_content,
                extracted_state=current_state,
                is_information_complete=False,
                clarifying_questions=clarifying_questions,
                recommendations=[],
                retrieval_trace=None,
                multi_metric_stressors=[],
                detected_interactions=[]
            )

        # 6. Execute Deterministic Multi-Metric Reasoning
        analysis = reasoning_engine.analyze(current_state, user_constraints=user_constraints)
        stressor_descriptions = [s.description for s in analysis.stressors]
        coupling_mechanisms = [f"{c.name}: {c.mechanism}" for c in analysis.cross_variable_couplings]

        # 7. Ground Candidates via Scientific RAG & Audit with Claim Safety
        recommendations: List[RecommendationOutput] = []
        overall_retrieval_sources: List[RetrievedEvidence] = []
        top_relevance_score = 0.0

        for cand in analysis.candidate_interventions:
            # Query scientific knowledge base
            rag_trace = rag_service.search(
                query=cand.rag_search_query,
                target_metrics=cand.affected_metrics,
                region_filter=current_state.land.region,
                top_k=2
            )

            if rag_trace.top_relevance_score > top_relevance_score:
                top_relevance_score = rag_trace.top_relevance_score

            # Convert retrieved chunks into schema
            retrieved_sources: List[RetrievedEvidence] = []
            for src in rag_trace.sources_retrieved:
                rep_change = src.quantified_claims[0].get("change_range") if src.quantified_claims else None
                evidence_item = RetrievedEvidence(
                    source_title=src.title,
                    organization=src.organization,
                    year=src.year,
                    document_type=src.document_type,
                    relevance_score=src.relevance_score,
                    evidence_text=src.evidence_text,
                    reported_change=rep_change,
                    doi_or_url=src.doi_or_url
                )
                retrieved_sources.append(evidence_item)
                overall_retrieval_sources.append(evidence_item)

            # Audit quantitative statements against retrieved chunks
            evidence_dicts = [s.model_dump() for s in rag_trace.sources_retrieved]
            audit_res = claim_safety_engine.audit_intervention_claim(
                claim_text=cand.description,
                retrieved_evidence_chunks=evidence_dicts,
                strict_mode=True
            )

            # Build explainable rationale steps
            why_steps = [
                f"Multi-Metric Trigger: Addressed stressors [{', '.join(cand.addresses_stressors)}].",
                f"Cross-Variable Balance: Positively acts across {len(cand.affected_metrics)} metrics simultaneously ({', '.join(cand.affected_metrics[:3])})."
            ]
            if audit_res.verified_citations:
                why_steps.append(f"Institutional Grounding: Backed by {', '.join(audit_res.verified_citations)}.")
            if user_constraints.get("cannot_change_main_crop"):
                why_steps.append("Constraint Preserved: Adapted as an in-situ strip/boundary strategy preserving 100% of primary cash crop acreage.")

            rec_output = RecommendationOutput(
                id=cand.id,
                title=cand.title,
                directive=audit_res.audited_text,
                scientific_rationale=" ".join(cand.rationale_points),
                environmental_metrics_affected=cand.affected_metrics,
                time_horizon=cand.time_horizon,
                confidence="High" if (rag_trace.top_relevance_score >= 0.80 and audit_res.grounding_status == "FULLY_GROUNDED") else "Medium",
                evidence=retrieved_sources,
                why_this_recommendation=why_steps,
                claim_type="evidence_supported_interval" if audit_res.grounding_status == "FULLY_GROUNDED" else "qualitative_estimate",
                reported_change=retrieved_sources[0].reported_change if retrieved_sources else None
            )
            recommendations.append(rec_output)

        # 8. Compose Grounded Assistant Message
        assistant_message = (
            f"### Comprehensive Ecological Diagnosis\n"
            f"{analysis.summary_diagnosis}\n\n"
            f"#### Active Cross-Variable Couplings:\n"
            + "\n".join([f"• **{c.name}**: {c.mechanism}" for c in analysis.cross_variable_couplings])
            + f"\n\n#### Scientifically Grounded Interventions ({len(recommendations)} Actions):\n"
            + "\n".join([
                f"**{i+1}. {r.title}** ({r.time_horizon}, Confidence: {r.confidence})\n"
                f"{r.directive}\n"
                f"*Rationale:* {r.scientific_rationale}\n"
                f"*Impacted Metrics:* {', '.join(r.environmental_metrics_affected)}\n"
                f"*Evidence:* {r.evidence[0].organization} ({r.evidence[0].year}) — {r.reported_change or 'Documented positive yield & ecological resilience'}\n"
                for i, r in enumerate(recommendations)
            ])
        )

        # 9. Persist into Database
        user_msg = ConversationMessage(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            extracted_state=current_state.model_dump()
        )
        asst_msg = ConversationMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_message,
            extracted_state=current_state.model_dump(),
            clarifications_requested=[]
        )
        db.add(user_msg)
        db.add(asst_msg)

        # If connected to a LandProfile, persist recommendations and metrics
        if conversation.land_profile_id:
            self._sync_land_profile(db, conversation.land_profile_id, current_state, recommendations)

        db.commit()

        # Construct RetrievalTrace for transparency
        global_trace = RetrievalTrace(
            query=request.message,
            filters_applied={
                "region": current_state.land.region,
                "crop": current_state.land.crop,
                "constraints": user_constraints
            },
            sources=overall_retrieval_sources[:4],
            top_score=top_relevance_score
        )

        return ChatResponse(
            conversation_id=conversation.id,
            message=assistant_message,
            extracted_state=current_state,
            is_information_complete=True,
            clarifying_questions=[],
            recommendations=recommendations,
            retrieval_trace=global_trace,
            multi_metric_stressors=stressor_descriptions,
            detected_interactions=coupling_mechanisms
        )

    def _reconstruct_state_from_history(self, conversation: Conversation) -> EnvironmentalState:
        accumulated_state = EnvironmentalState()
        # Sort messages chronologically
        for msg in conversation.messages:
            if msg.extracted_state:
                parsed = EnvironmentalState.model_validate(msg.extracted_state)
                accumulated_state = accumulated_state.merge_with(parsed)
        return accumulated_state

    def _sync_land_profile(
        self,
        db: Session,
        profile_id: str,
        state: EnvironmentalState,
        recommendations: List[RecommendationOutput]
    ):
        profile = db.query(LandProfile).filter(LandProfile.id == profile_id).first()
        if not profile:
            return

        if state.land.region:
            profile.region = state.land.region
        if state.land.crop:
            profile.primary_crop = state.land.crop
        if state.land.land_use:
            profile.farming_system = state.land.land_use

        # Add metric records
        if state.soil.model_dump(exclude_none=True):
            db.add(SoilMetric(
                land_profile_id=profile.id,
                organic_carbon_pct=state.soil.organic_carbon_pct,
                ph=state.soil.ph,
                moisture_pct=state.soil.moisture_pct,
                nitrogen_ppm=state.soil.nitrogen_ppm,
                texture=state.soil.texture
            ))

        if state.climate.model_dump(exclude_none=True):
            db.add(ClimateMetric(
                land_profile_id=profile.id,
                rainfall_category=state.climate.rainfall,
                annual_rainfall_mm=state.climate.annual_rainfall_mm,
                avg_temperature_celsius=state.climate.temperature_celsius,
                drought_frequency=state.climate.drought_frequency,
                water_availability=state.climate.water_availability
            ))

        if state.biodiversity.model_dump(exclude_none=True):
            db.add(BiodiversityMetric(
                land_profile_id=profile.id,
                species_richness_index=state.biodiversity.species_richness,
                habitat_diversity_index=state.biodiversity.habitat_diversity,
                pollinator_presence=state.biodiversity.pollinator_presence,
                native_plant_ratio=state.biodiversity.native_species_ratio
            ))

        if state.human_impact.model_dump(exclude_none=True):
            db.add(HumanImpactMetric(
                land_profile_id=profile.id,
                pesticide_intensity=state.human_impact.pesticide_use,
                water_extraction_rate=state.human_impact.water_extraction,
                deforestation_proximity=state.human_impact.deforestation_proximity
            ))

        # Save recommendations & sources
        for rec in recommendations:
            rec_db = Recommendation(
                land_profile_id=profile.id,
                title=rec.title,
                directive=rec.directive,
                scientific_rationale=rec.scientific_rationale,
                impacted_metrics=rec.environmental_metrics_affected,
                time_horizon=rec.time_horizon,
                confidence_level=rec.confidence,
                reasoning_trace=rec.why_this_recommendation
            )
            db.add(rec_db)
            db.flush()

            for src in rec.evidence:
                source_db = Source(
                    recommendation_id=rec_db.id,
                    title=src.source_title,
                    organization=src.organization,
                    year=src.year,
                    document_type=src.document_type,
                    evidence_snippet=src.evidence_text,
                    relevance_score=src.relevance_score,
                    doi_or_url=src.doi_or_url
                )
                db.add(source_db)

orchestrator = EcoMindOrchestrator()
