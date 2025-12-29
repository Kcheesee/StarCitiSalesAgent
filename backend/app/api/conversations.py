"""
Conversation API Routes
Handles all conversation-related endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from ..database import get_db
from ..services.ai_consultant import ConversationManager
from ..services.pdf_generator import generate_both_pdfs
from ..services.email_service import send_fleet_recommendations
from ..models import Conversation

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


# ============================================================================
# Pydantic Models (Request/Response)
# ============================================================================

class ConversationStartRequest(BaseModel):
    """Request to start a new conversation"""
    user_name: Optional[str] = Field(None, max_length=200)
    user_email: Optional[EmailStr] = None


class ConversationStartResponse(BaseModel):
    """Response when starting a new conversation"""
    conversation_id: int
    conversation_uuid: str
    status: str
    started_at: datetime
    message: str = "Conversation started! Ask me about Star Citizen ships."

    class Config:
        from_attributes = True


class MessageRequest(BaseModel):
    """Request to send a message"""
    message: str = Field(..., min_length=1, max_length=5000)
    force_recommendations: bool = Field(default=False)


class MessageResponse(BaseModel):
    """Response to a message"""
    conversation_id: int
    message: str
    phase: str
    has_recommendations: bool
    is_complete: bool
    recommended_ships: List[Dict[str, Any]]


class ConversationHistoryResponse(BaseModel):
    """Full conversation history"""
    conversation_id: int
    conversation_uuid: str
    status: str
    transcript: List[Dict[str, Any]]
    recommended_ships: List[Dict[str, Any]]
    user_email: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    last_message_at: datetime

    class Config:
        from_attributes = True


class CompleteConversationRequest(BaseModel):
    """Request to complete conversation and provide email"""
    user_email: EmailStr
    user_name: Optional[str] = None


class CompleteConversationResponse(BaseModel):
    """Response after completing conversation"""
    conversation_id: int
    status: str
    message: str = "Conversation completed! You'll receive your fleet guide via email."
    recommended_ships: List[Dict[str, Any]]
    pdf_urls: Dict[str, str] = {}


class GeneratePDFsResponse(BaseModel):
    """Response after generating PDFs"""
    conversation_id: int
    message: str
    transcript_pdf_url: str
    fleet_guide_pdf_url: str
    generated_at: datetime


class SendEmailRequest(BaseModel):
    """Request to send fleet recommendations email"""
    email: EmailStr
    name: Optional[str] = None


class SendEmailResponse(BaseModel):
    """Response after sending email"""
    conversation_id: int
    message: str
    email_sent_to: str
    sent_at: datetime


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/start", response_model=ConversationStartResponse, status_code=status.HTTP_201_CREATED)
def start_conversation(
    request: Optional[ConversationStartRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Start a new conversation session

    Args:
        request: Optional user name and email

    Returns:
        Conversation details and welcome message
    """
    try:
        manager = ConversationManager(db)
        conversation = manager.start_conversation()

        # Update user info if provided
        if request:
            if request.user_name:
                conversation.user_name = request.user_name
            if request.user_email:
                conversation.user_email = request.user_email
            db.commit()

        return ConversationStartResponse(
            conversation_id=conversation.id,
            conversation_uuid=str(conversation.conversation_uuid),
            status=conversation.status,
            started_at=conversation.started_at
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start conversation: {str(e)}"
        )


@router.post("/{conversation_id}/message", response_model=MessageResponse)
def send_message(
    conversation_id: int,
    request: MessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message in an existing conversation

    Args:
        conversation_id: ID of the conversation
        request: Message content

    Returns:
        AI response and conversation state
    """
    try:
        manager = ConversationManager(db)

        # Process message
        response = manager.process_message(
            conversation_id=conversation_id,
            user_message=request.message,
            force_recommendations=request.force_recommendations
        )

        return MessageResponse(**response)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=ConversationHistoryResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    Get conversation history and details

    Args:
        conversation_id: ID of the conversation

    Returns:
        Full conversation history
    """
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    return ConversationHistoryResponse(
        conversation_id=conversation.id,
        conversation_uuid=str(conversation.conversation_uuid),
        status=conversation.status,
        transcript=conversation.transcript or [],
        recommended_ships=conversation.recommended_ships or [],
        user_email=conversation.user_email,
        started_at=conversation.started_at,
        completed_at=conversation.completed_at,
        last_message_at=conversation.last_message_at
    )


@router.post("/{conversation_id}/complete", response_model=CompleteConversationResponse)
def complete_conversation(
    conversation_id: int,
    request: CompleteConversationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Mark conversation as complete, generate PDFs, and send email

    Args:
        conversation_id: ID of the conversation
        request: User email and name for PDF delivery
        background_tasks: FastAPI background tasks

    Returns:
        Completion confirmation with PDF URLs
    """
    try:
        manager = ConversationManager(db)
        conversation = manager.complete_conversation(
            conversation_id=conversation_id,
            user_email=request.user_email
        )

        # Update user name if provided
        if request.user_name:
            conversation.user_name = request.user_name
            db.commit()

        # Generate PDFs
        try:
            pdf_paths = generate_both_pdfs(conversation_id, db)
            db.refresh(conversation)
        except Exception as e:
            print(f"Warning: Failed to generate PDFs: {e}")
            # Continue even if PDF generation fails
            pdf_paths = {}

        # Send email in background
        if conversation.transcript_pdf_path and conversation.fleet_guide_pdf_path:
            ship_names = [ship.get("name", "Unknown") for ship in (conversation.recommended_ships or [])]

            background_tasks.add_task(
                send_fleet_recommendations,
                to_email=request.user_email,
                user_name=request.user_name,
                transcript_pdf_path=conversation.transcript_pdf_path,
                fleet_guide_pdf_path=conversation.fleet_guide_pdf_path,
                recommended_ships=ship_names
            )

        return CompleteConversationResponse(
            conversation_id=conversation.id,
            status=conversation.status,
            recommended_ships=conversation.recommended_ships or [],
            pdf_urls={
                "transcript": f"/api/conversations/{conversation_id}/transcript.pdf",
                "fleet_guide": f"/api/conversations/{conversation_id}/fleet-guide.pdf"
            } if conversation.transcript_pdf_path else {}
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete conversation: {str(e)}"
        )


@router.get("/{conversation_id}/recommendations")
def get_recommendations(conversation_id: int, db: Session = Depends(get_db)):
    """
    Get recommended ships for a conversation

    Args:
        conversation_id: ID of the conversation

    Returns:
        List of recommended ships with details
    """
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    return {
        "conversation_id": conversation.id,
        "recommended_ships": conversation.recommended_ships or [],
        "has_recommendations": len(conversation.recommended_ships or []) > 0
    }


@router.post("/{conversation_id}/generate-pdfs", response_model=GeneratePDFsResponse)
def generate_pdfs(
    conversation_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate transcript and fleet guide PDFs for a conversation

    Args:
        conversation_id: ID of the conversation
        background_tasks: FastAPI background tasks

    Returns:
        PDF download URLs
    """
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    try:
        # Generate PDFs (could be moved to background task for large conversations)
        pdf_paths = generate_both_pdfs(conversation_id, db)

        return GeneratePDFsResponse(
            conversation_id=conversation_id,
            message="PDFs generated successfully",
            transcript_pdf_url=f"/api/conversations/{conversation_id}/transcript.pdf",
            fleet_guide_pdf_url=f"/api/conversations/{conversation_id}/fleet-guide.pdf",
            generated_at=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDFs: {str(e)}"
        )


@router.get("/{conversation_id}/transcript.pdf")
def download_transcript_pdf(conversation_id: int, db: Session = Depends(get_db)):
    """
    Download conversation transcript PDF

    Args:
        conversation_id: ID of the conversation

    Returns:
        PDF file
    """
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    if not conversation.transcript_pdf_path or not os.path.exists(conversation.transcript_pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript PDF not found. Generate PDFs first using POST /{conversation_id}/generate-pdfs"
        )

    return FileResponse(
        path=conversation.transcript_pdf_path,
        media_type="application/pdf",
        filename=f"transcript_{conversation.conversation_uuid}.pdf"
    )


@router.get("/{conversation_id}/fleet-guide.pdf")
def download_fleet_guide_pdf(conversation_id: int, db: Session = Depends(get_db)):
    """
    Download fleet composition guide PDF

    Args:
        conversation_id: ID of the conversation

    Returns:
        PDF file
    """
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    if not conversation.fleet_guide_pdf_path or not os.path.exists(conversation.fleet_guide_pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fleet guide PDF not found. Generate PDFs first using POST /{conversation_id}/generate-pdfs"
        )

    return FileResponse(
        path=conversation.fleet_guide_pdf_path,
        media_type="application/pdf",
        filename=f"fleet_guide_{conversation.conversation_uuid}.pdf"
    )


@router.post("/{conversation_id}/send-email", response_model=SendEmailResponse)
def send_email(
    conversation_id: int,
    request: SendEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send fleet recommendations email with PDF attachments

    Args:
        conversation_id: ID of the conversation
        request: Email address to send to
        background_tasks: FastAPI background tasks

    Returns:
        Email confirmation
    """
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    # Check if PDFs exist, generate if needed
    if not conversation.transcript_pdf_path or not conversation.fleet_guide_pdf_path:
        try:
            generate_both_pdfs(conversation_id, db)
            # Refresh conversation object to get updated PDF paths
            db.refresh(conversation)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate PDFs: {str(e)}"
            )

    # Extract ship names for email
    ship_names = []
    if conversation.recommended_ships:
        for ship_data in conversation.recommended_ships:
            ship_names.append(ship_data.get("name", "Unknown Ship"))

    # Send email
    try:
        send_fleet_recommendations(
            to_email=request.email,
            user_name=request.name,
            transcript_pdf_path=conversation.transcript_pdf_path,
            fleet_guide_pdf_path=conversation.fleet_guide_pdf_path,
            recommended_ships=ship_names
        )

        # Update conversation with email and name
        conversation.user_email = request.email
        if request.name:
            conversation.user_name = request.name
        conversation.email_sent = True
        db.commit()

        return SendEmailResponse(
            conversation_id=conversation_id,
            message="Fleet recommendations sent successfully!",
            email_sent_to=request.email,
            sent_at=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    Delete a conversation (for testing/cleanup)

    Args:
        conversation_id: ID of the conversation

    Returns:
        Success message
    """
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    db.delete(conversation)
    db.commit()

    return {"message": f"Conversation {conversation_id} deleted successfully"}
