"""
Conversation models
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_uuid = Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        index=True
    )

    # User Info
    user_email = Column(String(255), index=True)
    user_budget_usd = Column(Integer)
    user_playstyle = Column(String(100))
    user_preferences = Column(JSON)  # JSONB

    # Conversation State
    status = Column(String(50), default="active", index=True)
    transcript = Column(JSON)  # JSONB array of messages

    # AI Recommendations
    recommended_ships = Column(JSON)  # JSONB array of ship recommendations

    # Generated Documents
    transcript_pdf_path = Column(String(500))
    fleet_guide_pdf_path = Column(String(500))

    # Email Delivery
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(TIMESTAMP)

    # Timestamps
    started_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    completed_at = Column(TIMESTAMP)
    last_message_at = Column(TIMESTAMP, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())
