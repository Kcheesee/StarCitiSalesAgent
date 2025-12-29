"""
AI Consultant Service - Core conversational logic
Manages conversations with Claude and ship recommendations via RAG
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import os
from dotenv import load_dotenv
from anthropic import Anthropic

from ..models import Conversation, Ship
from ..utils.prompts import (
    CONSULTANT_SYSTEM_PROMPT,
    REFINEMENT_PROMPT,
    COMPLETION_PROMPT,
    format_ships_for_context,
    detect_conversation_phase,
    ConversationPhase,
    build_search_query
)
from .rag_system import search_ships, hybrid_search

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Claude model to use
CLAUDE_MODEL = "claude-3-7-sonnet-20250219"


class ConversationManager:
    """
    Manages AI consultant conversations
    Handles message processing, RAG integration, and state management
    """

    def __init__(self, db: Session):
        self.db = db
        self.client = client

    def start_conversation(self) -> Conversation:
        """
        Start a new conversation session

        Returns:
            New Conversation object
        """
        conversation = Conversation(
            status="active",
            transcript=[],
            recommended_ships=[],
            started_at=datetime.utcnow(),
            last_message_at=datetime.utcnow()
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID"""
        return self.db.query(Conversation).filter_by(id=conversation_id).first()

    def process_message(
        self,
        conversation_id: int,
        user_message: str,
        force_recommendations: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user message and generate AI response

        Args:
            conversation_id: ID of the conversation
            user_message: User's message text
            force_recommendations: Force recommendation phase

        Returns:
            Dictionary with response and metadata
        """
        # Get conversation
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Get current transcript
        transcript = conversation.transcript or []

        # Detect conversation phase
        has_recommendations = len(conversation.recommended_ships or []) > 0
        phase = detect_conversation_phase(
            len(transcript),
            has_recommendations,
            user_message
        )

        # Search for relevant ships if appropriate
        ship_context = None
        if phase in [ConversationPhase.RECOMMENDATION, ConversationPhase.REFINEMENT] or force_recommendations:
            ship_context = self._search_ships_for_context(user_message, transcript)

        # Build Claude messages
        messages = self._build_claude_messages(transcript, user_message, ship_context, phase)

        # Call Claude
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                system=self._get_system_prompt(phase),
                messages=messages
            )

            # Extract response text
            assistant_message = response.content[0].text

            # Update transcript
            transcript.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            transcript.append({
                "role": "assistant",
                "content": assistant_message,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Extract recommended ships from response if in recommendation phase
            if phase == ConversationPhase.RECOMMENDATION and ship_context:
                self._extract_and_save_recommendations(conversation, ship_context, assistant_message)

            # Update conversation
            conversation.transcript = transcript
            conversation.last_message_at = datetime.utcnow()

            # Check if conversation is complete
            if phase == ConversationPhase.COMPLETION:
                conversation.status = "completed"
                conversation.completed_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(conversation)

            return {
                "conversation_id": conversation.id,
                "message": assistant_message,
                "phase": phase,
                "has_recommendations": len(conversation.recommended_ships or []) > 0,
                "is_complete": conversation.status == "completed",
                "recommended_ships": conversation.recommended_ships or []
            }

        except Exception as e:
            print(f"❌ Error calling Claude API: {e}")
            raise

    def _search_ships_for_context(self, user_message: str, transcript: List[Dict]) -> Optional[List[Dict]]:
        """
        Search for relevant ships based on conversation context

        Args:
            user_message: Latest user message
            transcript: Full conversation transcript

        Returns:
            List of relevant ship dictionaries or None
        """
        try:
            # Extract interests from conversation
            interests = self._extract_interests(user_message, transcript)

            # Build search query
            query = build_search_query(interests)

            # Extract filters from conversation
            filters = self._extract_filters(transcript)

            # Search ships
            ships = search_ships(
                self.db,
                query,
                top_k=8,
                min_similarity=0.5,
                filters=filters
            )

            return ships if ships else None

        except Exception as e:
            print(f"⚠️  RAG search failed: {e}")
            # Fallback: return some popular versatile ships
            return self._get_fallback_ships()

    def _extract_interests(self, user_message: str, transcript: List[Dict]) -> List[str]:
        """
        Extract user interests from conversation

        Args:
            user_message: Latest message
            transcript: Full transcript

        Returns:
            List of interest keywords
        """
        interests = []
        text = user_message.lower()

        # Check for playstyle keywords
        if any(word in text for word in ["combat", "fight", "battle", "bounty", "pvp"]):
            interests.append("combat")

        if any(word in text for word in ["trade", "trading", "cargo", "haul", "freight"]):
            interests.append("trading")

        if any(word in text for word in ["explore", "exploration", "discover", "scan"]):
            interests.append("exploration")

        if any(word in text for word in ["mine", "mining", "ore", "resource"]):
            interests.append("mining")

        if any(word in text for word in ["versatile", "multi", "all-around", "everything"]):
            interests.append("multi_role")

        if any(word in text for word in ["solo", "alone", "single"]):
            interests.append("solo")

        if any(word in text for word in ["crew", "group", "friends", "multi-crew"]):
            interests.append("group")

        if any(word in text for word in ["starter", "beginner", "first", "new"]):
            interests.append("starter")

        if any(word in text for word in ["luxury", "fancy", "premium", "nice"]):
            interests.append("luxury")

        # Default to multi-role if no specific interests
        if not interests:
            interests.append("multi_role")

        return interests

    def _extract_filters(self, transcript: List[Dict]) -> Dict[str, Any]:
        """
        Extract filters from conversation transcript

        Args:
            transcript: Conversation history

        Returns:
            Dictionary of filters
        """
        filters = {}

        # Combine all messages into one text for analysis
        all_text = " ".join([msg.get("content", "") for msg in transcript]).lower()

        # Budget extraction (simple keyword matching)
        if "under 100" in all_text or "< 100" in all_text or "less than 100" in all_text:
            filters["price_max"] = 100
        elif "under 200" in all_text or "< 200" in all_text or "under $200" in all_text:
            filters["price_max"] = 200
        elif "under 500" in all_text or "< 500" in all_text:
            filters["price_max"] = 500

        # Crew size for solo players
        if any(word in all_text for word in ["solo", "alone", "single player"]):
            filters["crew_max"] = 1

        # Cargo requirements
        if "cargo" in all_text or "haul" in all_text:
            filters["cargo_min"] = 20  # At least some cargo capability

        return filters

    def _get_fallback_ships(self) -> List[Dict]:
        """Get popular versatile ships as fallback"""
        # Return some popular multi-role ships manually
        popular_ships = ["Cutlass Black", "Freelancer", "Avenger Titan", "Constellation Andromeda"]

        ships = []
        for name in popular_ships:
            ship = self.db.query(Ship).filter(Ship.name.ilike(f"%{name}%")).first()
            if ship:
                ships.append({
                    "id": ship.id,
                    "name": ship.name,
                    "manufacturer": ship.manufacturer_name,
                    "focus": ship.focus,
                    "cargo_capacity": ship.cargo_capacity,
                    "crew_min": ship.crew_min,
                    "price_usd": float(ship.price_usd) if ship.price_usd else None,
                    "description": ship.description,
                    "similarity_score": 0.7  # Default score
                })

        return ships

    def _build_claude_messages(
        self,
        transcript: List[Dict],
        user_message: str,
        ship_context: Optional[List[Dict]],
        phase: str
    ) -> List[Dict]:
        """
        Build message array for Claude API

        Args:
            transcript: Conversation history
            user_message: Latest user message
            ship_context: Relevant ships from RAG
            phase: Current conversation phase

        Returns:
            List of message dictionaries
        """
        messages = []

        # Add conversation history
        for msg in transcript:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Build current user message with ship context if available
        current_content = user_message

        if ship_context and phase in [ConversationPhase.RECOMMENDATION, ConversationPhase.REFINEMENT]:
            ship_info = format_ships_for_context(ship_context, max_ships=6)
            current_content = f"{user_message}\n\n[AVAILABLE SHIPS FOR REFERENCE]\n{ship_info}"

        messages.append({
            "role": "user",
            "content": current_content
        })

        return messages

    def _get_system_prompt(self, phase: str) -> str:
        """Get appropriate system prompt based on conversation phase"""
        if phase == ConversationPhase.COMPLETION:
            return CONSULTANT_SYSTEM_PROMPT + "\n\n" + COMPLETION_PROMPT
        elif phase == ConversationPhase.REFINEMENT:
            return CONSULTANT_SYSTEM_PROMPT + "\n\n" + REFINEMENT_PROMPT
        else:
            return CONSULTANT_SYSTEM_PROMPT

    def _extract_and_save_recommendations(
        self,
        conversation: Conversation,
        ship_context: List[Dict],
        assistant_message: str
    ):
        """
        Extract ship recommendations from assistant response and save

        Args:
            conversation: Conversation object
            ship_context: Ships that were provided to Claude
            assistant_message: Claude's response
        """
        # Simple extraction: assume ships in context are the recommendations
        # In production, could use Claude to parse structured recommendations

        recommended_ships = []
        for i, ship in enumerate(ship_context[:4], 1):  # Top 4 ships
            # Check if ship is mentioned in response
            if ship["name"] in assistant_message:
                recommended_ships.append({
                    "ship_id": ship["id"],
                    "ship_name": ship["name"],
                    "manufacturer": ship["manufacturer"],
                    "slug": ship.get("slug", ""),
                    "priority": i,
                    "recommendation_reason": f"Matches user's interest in {ship.get('focus', 'versatile gameplay')}"
                })

        if recommended_ships:
            conversation.recommended_ships = recommended_ships

    def complete_conversation(self, conversation_id: int, user_email: str) -> Conversation:
        """
        Mark conversation as complete and save user email

        Args:
            conversation_id: Conversation ID
            user_email: User's email for PDF delivery

        Returns:
            Updated conversation
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        conversation.user_email = user_email
        conversation.status = "completed"
        conversation.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(conversation)

        return conversation


# Helper function for direct usage
def create_consultant(db: Session) -> ConversationManager:
    """
    Factory function to create a ConversationManager instance

    Args:
        db: Database session

    Returns:
        ConversationManager instance
    """
    return ConversationManager(db)
