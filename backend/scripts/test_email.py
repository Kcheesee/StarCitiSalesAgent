#!/usr/bin/env python3
"""
Test email sending with sample PDFs
Generates demo transcript and fleet guide, then sends test email
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.email_service import send_fleet_recommendations
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import os


def create_sample_transcript_pdf(output_path: str):
    """Create a sample transcript PDF"""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30
    )
    story.append(Paragraph("Conversation Transcript", title_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Sample conversation
    messages = [
        ("User", "Hi! I'm looking for a versatile ship for cargo hauling and some light combat."),
        ("Nova", "Great choice! I'd recommend looking at the Freelancer series. What's your budget?"),
        ("User", "Around $150-200 would be ideal."),
        ("Nova", "Perfect! The Freelancer MAX would be excellent for you. It has 120 SCU cargo and decent firepower."),
        ("User", "That sounds good! What about something for exploring?"),
        ("Nova", "For exploration, I'd suggest the Constellation Aquila or the 600i Explorer."),
        ("User", "I like the 600i! What else should I consider?"),
        ("Nova", "Based on your interests, here are my top 5 recommendations for a well-rounded fleet."),
    ]

    for speaker, text in messages:
        story.append(Paragraph(f"<b>{speaker}:</b> {text}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

    doc.build(story)
    print(f"✅ Created sample transcript: {output_path}")


def create_sample_fleet_guide_pdf(output_path: str):
    """Create a sample fleet guide PDF"""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30
    )
    story.append(Paragraph("Fleet Composition Guide", title_style))
    story.append(Paragraph(f"Prepared on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))

    # Recommended ships
    story.append(Paragraph("<b>Your Recommended Fleet:</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    ships = [
        {
            "name": "Freelancer MAX",
            "role": "Cargo Hauling",
            "reason": "Best cargo capacity in your budget with solid defensive capabilities"
        },
        {
            "name": "600i Explorer",
            "role": "Exploration",
            "reason": "Luxury explorer with excellent range and scanning capabilities"
        },
        {
            "name": "Cutlass Black",
            "role": "Multi-Role",
            "reason": "Versatile ship perfect for bounty hunting and light cargo"
        },
        {
            "name": "Prospector",
            "role": "Mining",
            "reason": "Efficient solo mining ship for supplemental income"
        },
        {
            "name": "Arrow",
            "role": "Light Fighter",
            "reason": "Nimble fighter for combat missions and defense"
        }
    ]

    for i, ship in enumerate(ships, 1):
        story.append(Paragraph(f"<b>{i}. {ship['name']}</b> - {ship['role']}", styles['Heading3']))
        story.append(Paragraph(ship['reason'], styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("<b>Next Steps:</b>", styles['Heading2']))
    story.append(Paragraph(
        "Visit the RSI Pledge Store to purchase these ships. Start with the Cutlass Black "
        "as your daily driver, then expand your fleet based on your gameplay preferences.",
        styles['Normal']
    ))

    doc.build(story)
    print(f"✅ Created sample fleet guide: {output_path}")


def test_email_sending(recipient_email: str):
    """Test email sending with sample PDFs"""

    print("=" * 80)
    print("EMAIL SENDING TEST")
    print("=" * 80)
    print()

    # Create outputs directory if it doesn't exist
    outputs_dir = Path(__file__).parent.parent.parent / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    # Generate sample PDFs
    transcript_path = str(outputs_dir / "test_transcript.pdf")
    fleet_guide_path = str(outputs_dir / "test_fleet_guide.pdf")

    print("📄 Generating sample PDFs...")
    create_sample_transcript_pdf(transcript_path)
    create_sample_fleet_guide_pdf(fleet_guide_path)
    print()

    # Sample ship names
    recommended_ships = [
        "Freelancer MAX",
        "600i Explorer",
        "Cutlass Black",
        "Prospector",
        "Arrow"
    ]

    # Send test email
    print(f"📧 Sending test email to: {recipient_email}")
    print()

    try:
        success = send_fleet_recommendations(
            to_email=recipient_email,
            user_name="Test User",
            transcript_pdf_path=transcript_path,
            fleet_guide_pdf_path=fleet_guide_path,
            recommended_ships=recommended_ships
        )

        if success:
            print()
            print("=" * 80)
            print("✅ TEST SUCCESSFUL!")
            print("=" * 80)
            print()
            print("Check your email inbox for:")
            print("  📧 Subject: 'Your StarCiti Fleet Recommendations'")
            print("  📎 Attachments: conversation_transcript.pdf, fleet_composition_guide.pdf")
            print()
            print("If you don't see it:")
            print("  - Check your spam folder")
            print("  - Verify SendGrid API key is correct")
            print("  - Verify sender email is verified in SendGrid")
            print()

            # Cleanup
            print("🗑️  Cleaning up test PDFs...")
            os.remove(transcript_path)
            os.remove(fleet_guide_path)
            print("✅ Test files removed")

        else:
            print()
            print("=" * 80)
            print("⚠️  EMAIL SENT WITH WARNINGS")
            print("=" * 80)
            print("Check the output above for details")

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("  1. SENDGRID_API_KEY not set in .env")
        print("  2. Invalid SendGrid API key")
        print("  3. Sender email not verified in SendGrid")
        print("  4. SendGrid account suspended or rate limited")
        print()

        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print()
    print("🧪 StarCiti Sales Agent - Email Test")
    print()

    # Get recipient email
    if len(sys.argv) > 1:
        recipient = sys.argv[1]
    else:
        recipient = input("Enter recipient email address: ").strip()

    if not recipient or '@' not in recipient:
        print("❌ Invalid email address")
        sys.exit(1)

    test_email_sending(recipient)
