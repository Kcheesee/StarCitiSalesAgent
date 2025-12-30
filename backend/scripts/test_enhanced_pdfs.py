#!/usr/bin/env python3
"""
Test Enhanced PDF Generator
Creates a conversation with real ship data and generates SC-themed PDFs
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.conversation import Conversation
from app.models.ship import Ship
from app.services.pdf_generator_premium import generate_both_pdfs_premium as generate_both_pdfs
from datetime import datetime
import shutil

def create_test_conversation_with_ships(db):
    """Create a test conversation with real ship recommendations"""

    # Get 5 random ships from the database (not just first 5)
    from sqlalchemy import func
    ships = db.query(Ship).order_by(func.random()).limit(5).all()

    if not ships:
        print("❌ No ships found in database!")
        print("Run: python scripts/setup_database.py first")
        return None

    # Create recommended_ships JSON with real ship data
    recommended_ships = []
    for ship in ships:
        recommended_ships.append({
            "id": ship.id,  # CRITICAL: PDF generator needs this to look up ship
            "name": ship.name,
            "manufacturer": ship.manufacturer.name if ship.manufacturer else "Unknown",
            "role": ship.type or "Multi-Role",
            "focus": ship.focus or "General Purpose",
            "price_usd": ship.price_usd,
            "reason": f"Excellent {ship.type or 'multi-role'} ship with {ship.cargo_capacity or 0} SCU cargo capacity."
        })

    # Create transcript
    transcript = [
        {
            "role": "user",
            "content": "Hi! I'm looking for a versatile fleet for cargo hauling and exploration.",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "assistant",
            "content": f"Great choice! Based on your needs, I recommend the {ships[0].name}. What's your budget?",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "user",
            "content": "Around $500-1000 would be ideal.",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "assistant",
            "content": f"Perfect! I've put together a fleet of {len(ships)} ships that will serve you well.",
            "timestamp": datetime.now().isoformat()
        }
    ]

    # Create user preferences
    user_preferences = {
        "budget_min": 500,
        "budget_max": 1000,
        "playstyle": ["cargo", "exploration"],
        "crew_size": "solo",
        "priority": "versatility"
    }

    # Create conversation
    conversation = Conversation(
        user_name="Test Citizen",
        user_email="test@starciti.com",
        user_budget_usd=1000,
        user_playstyle="cargo_exploration",
        user_preferences=user_preferences,
        status="completed",
        transcript=transcript,
        recommended_ships=recommended_ships,
        completed_at=datetime.now()
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    print(f"✅ Created test conversation ID: {conversation.id}")
    print(f"   Ships recommended: {[s['name'] for s in recommended_ships]}")

    return conversation


def test_enhanced_pdfs():
    """Test the enhanced PDF generator"""

    print("=" * 80)
    print("ENHANCED PDF GENERATOR TEST")
    print("=" * 80)
    print()

    db = SessionLocal()

    try:
        # Create test conversation
        print("📝 Creating test conversation with real ship data...")
        conversation = create_test_conversation_with_ships(db)

        if not conversation:
            return

        print()
        print("📄 Generating enhanced Star Citizen themed PDFs...")

        # Generate PDFs
        pdf_paths = generate_both_pdfs(conversation.id, db)

        print()
        print(f"✅ Generated PDFs:")
        print(f"   Transcript: {pdf_paths['transcript_pdf']}")
        print(f"   Fleet Guide: {pdf_paths['fleet_guide_pdf']}")

        # Copy to Desktop
        desktop = Path("/Users/jackalmac/Desktop")

        transcript_dest = desktop / "StarCiti_Enhanced_Transcript.pdf"
        fleet_guide_dest = desktop / "StarCiti_Enhanced_Fleet_Guide.pdf"

        shutil.copy(pdf_paths['transcript_pdf'], transcript_dest)
        shutil.copy(pdf_paths['fleet_guide_pdf'], fleet_guide_dest)

        print()
        print("=" * 80)
        print("✅ SUCCESS!")
        print("=" * 80)
        print()
        print("Enhanced PDFs copied to Desktop:")
        print(f"  📄 {transcript_dest.name}")
        print(f"  📄 {fleet_guide_dest.name}")
        print()
        print("Features:")
        print("  ✓ Star Citizen color scheme (cyan #00BFFF, navy #1a2332, gold #FFB600)")
        print("  ✓ SC-themed headers (◆ MISSION PROFILE, etc.)")
        print("  ✓ Detailed ship specifications tables:")
        print("    - Dimensions & Mass")
        print("    - Performance (speed, acceleration)")
        print("    - Operational (crew, cargo, shields)")
        print("  ✓ Fleet strategic analysis")
        print("  ✓ Professional 'See you in the 'verse' footer")
        print()

        # Clean up test conversation
        print("🗑️  Cleaning up test conversation...")
        db.delete(conversation)
        db.commit()
        print("✅ Test data removed")

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()

        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    test_enhanced_pdfs()
