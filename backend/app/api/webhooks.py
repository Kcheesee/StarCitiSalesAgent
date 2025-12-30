"""
Webhook endpoints for external service integrations
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Dict, Any, List
import os
import hmac
import hashlib
from datetime import datetime

from ..database import get_db
from ..models import Conversation
from ..services.ship_analyzer import analyze_conversation_for_ships
from ..services.pdf_generator_premium import generate_both_pdfs_premium as generate_both_pdfs
from ..services.email_service import send_fleet_recommendations
from ..config import settings

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def verify_elevenlabs_signature(body: bytes, signature: str, secret: str) -> bool:
    """
    Verify HMAC signature from ElevenLabs webhook

    Args:
        body: Raw request body bytes
        signature: Signature from ElevenLabs-Signature header
        secret: Webhook secret from ElevenLabs dashboard

    Returns:
        True if signature is valid, False otherwise
    """
    if not secret:
        print("⚠️  Warning: No webhook secret configured, skipping signature verification")
        return True  # Allow in development without secret

    # Compute HMAC-SHA256 of the request body
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()

    # Compare signatures (constant-time comparison to prevent timing attacks)
    return hmac.compare_digest(expected_signature, signature)


@router.post("/elevenlabs/post-call")
async def elevenlabs_post_call_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receive post-call webhook from ElevenLabs after conversation ends

    Payload structure:
    {
        "type": "post_call_transcription",
        "event_timestamp": 1234567890,
        "data": {
            "agent_id": "agent_xxx",
            "conversation_id": "conv_xxx",
            "status": "done",
            "user_id": "user_xxx",
            "transcript": [
                {"role": "user", "message": "...", "time": 1234567890},
                {"role": "assistant", "message": "...", "time": 1234567891}
            ],
            "metadata": {...},
            "analysis": {...}
        }
    }
    """
    try:
        # Get raw request body for signature verification
        body = await request.body()

        # Verify HMAC signature
        signature = request.headers.get("elevenlabs-signature") or request.headers.get("x-elevenlabs-signature")

        if signature and settings.ELEVENLABS_WEBHOOK_SECRET:
            if not verify_elevenlabs_signature(body, signature, settings.ELEVENLABS_WEBHOOK_SECRET):
                print(f"❌ Invalid webhook signature!")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid webhook signature"
                )
            print(f"✅ Webhook signature verified")
        elif not signature:
            print(f"⚠️  No signature provided in headers")

        # Parse webhook payload
        payload = await request.json()

        # Verify webhook type
        if payload.get("type") != "post_call_transcription":
            print(f"Ignoring webhook type: {payload.get('type')}")
            return {"status": "ignored", "reason": "not transcription webhook"}

        # Extract data
        data = payload.get("data", {})
        elevenlabs_conversation_id = data.get("conversation_id")
        transcript = data.get("transcript", [])
        analysis = data.get("analysis", {})
        metadata = data.get("metadata", {})

        if not elevenlabs_conversation_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing conversation_id in webhook payload"
            )

        print(f"📞 Received ElevenLabs webhook for conversation: {elevenlabs_conversation_id}")
        print(f"   Transcript turns: {len(transcript)}")

        # Find our conversation record by matching user email or recent conversations
        # For now, we'll find the most recent active conversation
        # TODO: Better matching strategy - could store elevenlabs_conversation_id when starting
        conversation = db.query(Conversation).filter(
            Conversation.status.in_(["active", "completed"])
        ).order_by(
            Conversation.started_at.desc()
        ).first()

        if not conversation:
            print(f"⚠️  No conversation found to match ElevenLabs conversation {elevenlabs_conversation_id}")
            return {
                "status": "warning",
                "message": "No matching conversation found in database"
            }

        print(f"   Matched to database conversation: {conversation.id}")

        # Format transcript for database
        formatted_transcript = []
        for turn in transcript:
            formatted_transcript.append({
                "role": turn.get("role", "unknown"),
                "content": turn.get("message", ""),
                "timestamp": turn.get("time", 0)
            })

        # Update conversation with transcript
        conversation.transcript = formatted_transcript

        # Analyze conversation to extract ship recommendations
        print(f"   Analyzing conversation for ship mentions...")
        try:
            recommended_ships = analyze_conversation_for_ships(
                transcript=formatted_transcript,
                analysis=analysis,
                db=db
            )

            if recommended_ships:
                conversation.recommended_ships = recommended_ships
                print(f"   ✅ Found {len(recommended_ships)} ship recommendations")
            else:
                print(f"   ⚠️  No ships mentioned in conversation")
                # Set empty array instead of None
                conversation.recommended_ships = []
        except Exception as e:
            print(f"   ❌ Error analyzing conversation: {e}")
            conversation.recommended_ships = []

        # Mark as completed if not already
        if conversation.status == "active":
            conversation.status = "completed"
            conversation.completed_at = datetime.utcnow()

        # Save to database
        db.commit()
        db.refresh(conversation)

        print(f"   💾 Saved transcript and recommendations to database")

        # Generate PDFs and send email in background
        background_tasks.add_task(
            generate_pdfs_and_send_email,
            conversation_id=conversation.id,
            db_session=db
        )

        print(f"   📧 Queued PDF generation and email delivery")

        return {
            "status": "success",
            "conversation_id": conversation.id,
            "transcript_turns": len(formatted_transcript),
            "recommended_ships": len(conversation.recommended_ships or [])
        }

    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


def generate_pdfs_and_send_email(conversation_id: int, db_session: Session):
    """
    Background task to generate PDFs and send email after webhook processing
    """
    try:
        print(f"📄 Generating PDFs for conversation {conversation_id}...")

        # Generate PDFs
        pdf_paths = generate_both_pdfs(conversation_id, db_session)
        db_session.refresh(
            db_session.query(Conversation).filter_by(id=conversation_id).first()
        )

        conversation = db_session.query(Conversation).filter_by(id=conversation_id).first()

        if conversation and conversation.user_email:
            # Send email
            ship_names = [
                ship.get("name", "Unknown")
                for ship in (conversation.recommended_ships or [])
            ]

            print(f"📧 Sending email to {conversation.user_email}...")
            send_fleet_recommendations(
                to_email=conversation.user_email,
                user_name=conversation.user_name or "Pilot",
                transcript_pdf_path=conversation.transcript_pdf_path,
                fleet_guide_pdf_path=conversation.fleet_guide_pdf_path,
                recommended_ships=ship_names
            )

            conversation.email_sent = True
            conversation.email_sent_at = datetime.utcnow()
            db_session.commit()

            print(f"✅ Email sent successfully to {conversation.user_email}")
        else:
            print(f"⚠️  No email address found for conversation {conversation_id}")

    except Exception as e:
        print(f"❌ Error in background task: {str(e)}")
        import traceback
        traceback.print_exc()
