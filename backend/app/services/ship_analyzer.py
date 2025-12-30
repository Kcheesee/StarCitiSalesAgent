"""
Ship Analyzer Service
Analyzes conversation transcripts to extract ship mentions and generate recommendations
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
import os
from anthropic import Anthropic

from ..models import Ship

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def analyze_conversation_for_ships(
    transcript: List[Dict[str, Any]],
    analysis: Dict[str, Any],
    db: Session
) -> List[Dict[str, Any]]:
    """
    Analyze conversation transcript to extract ship mentions and recommendations

    Args:
        transcript: List of conversation turns with role and message
        analysis: Analysis data from ElevenLabs
        db: Database session

    Returns:
        List of recommended ships with metadata
    """
    if not transcript:
        return []

    # Build conversation text
    conversation_text = "\n\n".join([
        f"{turn['role'].upper()}: {turn.get('content', turn.get('message', ''))}"
        for turn in transcript
    ])

    # Use Claude to extract ship names and user preferences
    try:
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Analyze this Star Citizen ship consultation conversation and extract:
1. Ship names mentioned by the AI consultant
2. User's stated budget (if mentioned)
3. User's playstyle preferences (combat, cargo, exploration, etc.)
4. User's crew size preference

Conversation:
{conversation_text}

Respond with a JSON object in this exact format:
{{
    "ship_names": ["Ship Name 1", "Ship Name 2"],
    "user_budget": 500,
    "user_playstyle": "combat and exploration",
    "crew_size": "solo to 3 players"
}}

If information is not mentioned, use null for that field.
ONLY return the JSON object, no additional text."""
            }]
        )

        # Parse Claude's response
        response_text = response.content[0].text.strip()

        # Extract JSON from response (handle potential markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        import json
        extracted_data = json.loads(response_text)

        ship_names = extracted_data.get("ship_names", [])
        user_budget = extracted_data.get("user_budget")
        user_playstyle = extracted_data.get("user_playstyle")

        if not ship_names:
            print("No ship names extracted from conversation")
            return []

        # Look up ships in database
        recommended_ships = []
        for ship_name in ship_names:
            # Try exact match first
            ship = db.query(Ship).filter(Ship.name.ilike(f"%{ship_name}%")).first()

            if ship:
                recommended_ships.append({
                    "ship_id": ship.id,
                    "name": ship.name,
                    "manufacturer": ship.manufacturer_name or "Unknown",
                    "slug": ship.slug,
                    "focus": ship.focus,
                    "type": ship.type,
                    "cargo_capacity": ship.cargo_capacity,
                    "crew_min": ship.crew_min,
                    "crew_max": ship.crew_max,
                    "price_usd": ship.price_usd,
                    "recommendation_reason": f"Recommended based on user's {user_playstyle or 'requirements'}"
                })

        # If no ships found in database, create placeholder recommendations
        if not recommended_ships and ship_names:
            for i, ship_name in enumerate(ship_names[:5], 1):
                recommended_ships.append({
                    "ship_id": None,
                    "name": ship_name,
                    "manufacturer": "Unknown",
                    "slug": ship_name.lower().replace(" ", "-"),
                    "focus": user_playstyle or "Multi-role",
                    "priority": i,
                    "recommendation_reason": f"Mentioned in conversation as suitable for {user_playstyle or 'your needs'}"
                })

        return recommended_ships

    except Exception as e:
        print(f"Error analyzing conversation with Claude: {e}")
        import traceback
        traceback.print_exc()

        # Fallback: Try simple keyword matching
        return extract_ships_by_keyword_matching(transcript, db)


def extract_ships_by_keyword_matching(
    transcript: List[Dict[str, Any]],
    db: Session
) -> List[Dict[str, Any]]:
    """
    Fallback method: Extract ships by looking for ship names in the transcript

    Args:
        transcript: List of conversation turns
        db: Database session

    Returns:
        List of ships mentioned
    """
    # Get all ships from database
    all_ships = db.query(Ship).all()

    conversation_text = " ".join([
        turn.get('content', turn.get('message', '')).lower()
        for turn in transcript
    ])

    found_ships = []
    for ship in all_ships:
        ship_name_lower = ship.name.lower()
        if ship_name_lower in conversation_text:
            found_ships.append({
                "ship_id": ship.id,
                "name": ship.name,
                "manufacturer": ship.manufacturer_name or "Unknown",
                "slug": ship.slug,
                "focus": ship.focus,
                "type": ship.type,
                "cargo_capacity": ship.cargo_capacity,
                "crew_min": ship.crew_min,
                "crew_max": ship.crew_max,
                "price_usd": ship.price_usd,
                "recommendation_reason": "Mentioned in conversation"
            })

    # Return top 5 most mentioned
    return found_ships[:5]
