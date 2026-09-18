from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from backend.app.database.session import get_db
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.models.conversation import Conversation, ConversationMessage
from backend.app.services.orchestrator import orchestrator

router = APIRouter(prefix="/chat", tags=["Chat & Conversational Reasoning"])

@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def send_chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main conversational endpoint:
    - Extracts multi-variable environmental metrics (Soil, Climate, Land, Biodiversity, Human Impact).
    - Maintains conversational state memory across turns.
    - If information is incomplete, generates targeted clarifying questions.
    - If complete, executes deterministic multi-metric reasoning, retrieves grounded RAG citations (FAO, IPCC, ICRAF, ICRISAT),
      audits quantitative claims with claim safety, and returns actionable recommendations.
    """
    try:
        response = orchestrator.handle_chat_turn(db, request)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing conversational reasoning: {str(e)}"
        )

@router.get("/history/{conversation_id}")
def get_conversation_history(conversation_id: str, db: Session = Depends(get_db)):
    """
    Retrieves full message history and accumulated environmental state for a conversation.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "extracted_state": msg.extracted_state,
            "clarifications_requested": msg.clarifications_requested or [],
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        }
        for msg in conversation.messages
    ]

    accumulated_state = orchestrator._reconstruct_state_from_history(conversation)

    return {
        "conversation_id": conversation.id,
        "land_profile_id": conversation.land_profile_id,
        "current_state": accumulated_state.model_dump(),
        "messages": messages
    }

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Deletes a conversation session and resets memory.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    return {"message": "Conversation successfully deleted", "conversation_id": conversation_id}
