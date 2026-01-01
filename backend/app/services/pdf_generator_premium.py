"""
Premium PDF Generator using HTML Templates
Renders beautiful HTML templates to PDF using Playwright
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.conversation import Conversation
from app.models.ship import Ship


def _extract_preferences_from_transcript(transcript: List[Dict]) -> Dict[str, Any]:
    """Extract user preferences from conversation transcript"""
    preferences = {
        "budget": "Flexible",
        "playstyle": "Versatile",
        "crew_size": "Any",
        "primary_activities": ["General Operations"]
    }

    # Simple keyword extraction from user messages
    user_messages = " ".join([msg.get("content", "") for msg in transcript if msg.get("role") == "user"]).lower()

    # Budget detection
    if "100" in user_messages or "cheap" in user_messages or "budget" in user_messages:
        preferences["budget"] = "Under $100"
    elif "500" in user_messages or "mid" in user_messages:
        preferences["budget"] = "$100-500"
    elif "expensive" in user_messages or "high" in user_messages or "1000" in user_messages:
        preferences["budget"] = "$500+"

    # Crew size
    if "solo" in user_messages or "alone" in user_messages or "single" in user_messages:
        preferences["crew_size"] = "Solo"
    elif "multi" in user_messages or "crew" in user_messages or "friends" in user_messages:
        preferences["crew_size"] = "Multi-Crew"

    # Activities
    activities = []
    if "cargo" in user_messages or "hauling" in user_messages or "trading" in user_messages:
        activities.append("Cargo & Trading")
    if "exploration" in user_messages or "exploring" in user_messages:
        activities.append("Exploration")
    if "combat" in user_messages or "fighting" in user_messages or "bounty" in user_messages:
        activities.append("Combat")
    if "mining" in user_messages:
        activities.append("Mining")

    if activities:
        preferences["primary_activities"] = activities

    return preferences


def _generate_fleet_analysis(ships: List[Dict], preferences: Dict) -> str:
    """Generate strategic fleet analysis"""
    if not ships:
        return "No vessels have been recommended at this time. Continue your consultation with Nova to receive personalized ship recommendations."

    ship_count = len(ships)
    roles = set([ship.get("focus", "Multi-Role") for ship in ships])
    total_cargo = sum([ship.get("cargo_capacity", 0) for ship in ships])

    analysis = f"This {ship_count}-ship fleet provides comprehensive coverage across {len(roles)} operational roles. "
    analysis += f"Combined cargo capacity of {total_cargo:,} SCU enables significant trading operations. "

    crew_min = sum([ship.get("crew_min", 1) for ship in ships])
    crew_max = sum([ship.get("crew_max", 1) for ship in ships])

    analysis += f"Fleet requires {crew_min}-{crew_max} crew members for full operation, offering excellent scalability from solo to multi-crew gameplay. "

    analysis += f"Recommended deployment strategy: Start with your most versatile vessel and expand operations as you build experience and resources."

    return analysis


def generate_fleet_guide_pdf_premium(conversation_id: int, db: Session) -> str:
    """
    Generate premium fleet guide PDF from HTML template

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Path to generated PDF
    """
    # Get conversation
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise ValueError(f"Conversation {conversation_id} not found")
    
    # Refresh to get latest data (in case webhook just updated it)
    db.refresh(conversation)
    
    print(f"🔍 DEBUG FLEET: Conversation has {len(conversation.recommended_ships or [])} ships")

    # Get ship details from recommended_ships
    ships_data = []
    if conversation.recommended_ships:
        for ship_rec in conversation.recommended_ships:
            ship_id = ship_rec.get("ship_id")  # Fixed: was looking for "id" instead of "ship_id"
            if ship_id:
                ship = db.query(Ship).filter(Ship.id == ship_id).first()
                if ship:
                    ships_data.append({
                        "name": ship.name,
                        "manufacturer": ship.manufacturer.name if ship.manufacturer else "Unknown",
                        "focus": ship.focus or "Multi-Role",
                        "type": ship.type or "Multi-Role",
                        "price_usd": ship.price_usd,
                        "description": ship.description or "A versatile spacecraft designed for the modern space citizen.",
                        "reason": ship_rec.get("reason", "Recommended based on your preferences"),
                        "crew_min": ship.crew_min or 1,
                        "crew_max": ship.crew_max or ship.crew_min or 1,
                        "cargo_capacity": ship.cargo_capacity or 0,
                        "speed_scm": ship.speed_scm,
                        "speed_max": ship.speed_max,
                    })

    # Extract preferences
    preferences = _extract_preferences_from_transcript(conversation.transcript or [])

    # Generate fleet analysis
    fleet_analysis = _generate_fleet_analysis(ships_data, preferences)

    # Prepare template context
    context = {
        "user_name": conversation.user_name,
        "user_email": conversation.user_email,
        "conversation_uuid": str(conversation.conversation_uuid),
        "generated_date": datetime.now().strftime("%B %d, %Y"),
        "budget_range": preferences["budget"],
        "playstyle": preferences["playstyle"],
        "crew_preference": preferences["crew_size"],
        "primary_activities": ", ".join(preferences["primary_activities"]),
        "fleet_analysis": fleet_analysis,
        "ships": ships_data,
        "total_ships": len(ships_data),
    }

    # Setup Jinja2 environment
    template_dir = Path(__file__).parent.parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("fleet_guide_premium.html")

    # Render HTML
    html_content = template.render(**context)

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent.parent / "outputs" / "fleet_guides"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate PDF using Playwright
    pdf_path = output_dir / f"fleet_guide_{conversation.conversation_uuid}.pdf"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
        )
        browser.close()

    print(f"✅ Generated premium fleet guide PDF: {pdf_path}")
    return str(pdf_path)


def generate_transcript_pdf_premium(conversation_id: int, db: Session) -> str:
    """
    Generate premium transcript PDF from HTML template

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Path to generated PDF
    """
    # Get conversation
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise ValueError(f"Conversation {conversation_id} not found")
    
    # Refresh to get latest data (in case webhook just updated it)
    db.refresh(conversation)
    
    print(f"🔍 DEBUG TRANSCRIPT: Conversation has {len(conversation.transcript or [])} turns")

    # Format messages
    messages = []
    if conversation.transcript:
        for msg in conversation.transcript:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp", "")
            })

    # Prepare template context
    context = {
        "conversation_uuid": str(conversation.conversation_uuid),
        "user_email": conversation.user_email or "Unknown",
        "total_messages": len(messages),
        "started_at": conversation.started_at.strftime("%B %d, %Y %I:%M %p") if conversation.started_at else "Unknown",
        "completed_at": conversation.completed_at.strftime("%B %d, %Y %I:%M %p") if conversation.completed_at else "In Progress",
        "generated_date": datetime.now().strftime("%B %d, %Y"),
        "messages": messages,
    }

    # Setup Jinja2 environment
    template_dir = Path(__file__).parent.parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("transcript_premium.html")

    # Render HTML
    html_content = template.render(**context)

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent.parent / "outputs" / "transcripts"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate PDF using Playwright
    pdf_path = output_dir / f"transcript_{conversation.conversation_uuid}.pdf"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
        )
        browser.close()

    print(f"✅ Generated premium transcript PDF: {pdf_path}")
    return str(pdf_path)


def generate_both_pdfs_premium(conversation_id: int, db: Session) -> Dict[str, str]:
    """
    Generate both premium PDFs (transcript and fleet guide)

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Dictionary with paths to both PDFs
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise ValueError(f"Conversation {conversation_id} not found")

    # Generate both PDFs
    transcript_path = generate_transcript_pdf_premium(conversation_id, db)
    fleet_guide_path = generate_fleet_guide_pdf_premium(conversation_id, db)

    # Update conversation with PDF paths
    conversation.transcript_pdf_path = transcript_path
    conversation.fleet_guide_pdf_path = fleet_guide_path
    db.commit()

    return {
        "transcript_pdf": transcript_path,
        "fleet_guide_pdf": fleet_guide_path
    }


if __name__ == "__main__":
    # Test the premium PDF generator
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        # Use conversation ID from command line or default
        conv_id = int(sys.argv[1]) if len(sys.argv) > 1 else 38
        print(f"Generating premium PDFs for conversation {conv_id}...")

        paths = generate_both_pdfs_premium(conv_id, db)
        print(f"\n✅ SUCCESS!")
        print(f"Transcript: {paths['transcript_pdf']}")
        print(f"Fleet Guide: {paths['fleet_guide_pdf']}")

    finally:
        db.close()
