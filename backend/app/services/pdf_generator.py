"""
PDF Generator Service
Creates professional PDFs for conversation transcripts and fleet guides using ReportLab
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from ..models.ship import Ship
from ..models.conversation import Conversation


# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "outputs"

# Ensure output directories exist
(OUTPUT_DIR / "transcripts").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "fleet_guides").mkdir(parents=True, exist_ok=True)

# Color scheme
BLUE = colors.HexColor("#2563eb")
GREEN = colors.HexColor("#10b981")
GRAY = colors.HexColor("#64748b")
LIGHT_GRAY = colors.HexColor("#f8fafc")


def generate_transcript_pdf(
    conversation: Conversation,
    output_path: Optional[str] = None
) -> str:
    """
    Generate conversation transcript PDF using ReportLab

    Args:
        conversation: Conversation object with messages
        output_path: Optional custom output path

    Returns:
        Path to generated PDF file
    """
    if not output_path:
        filename = f"transcript_{conversation.conversation_uuid}.pdf"
        output_path = str(OUTPUT_DIR / "transcripts" / filename)

    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=BLUE,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=GRAY,
        spaceAfter=20,
        alignment=TA_CENTER
    )

    # Header
    story.append(Paragraph("StarCiti Sales Agent", title_style))
    story.append(Paragraph("Conversation Transcript", subtitle_style))
    story.append(Spacer(1, 0.3*inch))

    # Meta information table
    meta_data = [
        ["Conversation ID:", str(conversation.conversation_uuid)],
        ["Started:", conversation.started_at.strftime("%B %d, %Y at %I:%M %p")],
        ["Completed:", conversation.completed_at.strftime("%B %d, %Y at %I:%M %p") if conversation.completed_at else "In Progress"],
        ["Contact Email:", conversation.user_email or "Not provided"],
    ]

    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY),
        ('TEXTCOLOR', (0, 0), (0, -1), GRAY),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4*inch))

    # Conversation messages
    story.append(Paragraph("Conversation History", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    if conversation.conversation_transcript:
        for msg in conversation.conversation_transcript:
            role = msg.get("role", "")
            content = msg.get("content", "")

            # Role label
            role_style = ParagraphStyle(
                'Role',
                parent=styles['Normal'],
                fontSize=11,
                textColor=GREEN if role == "user" else BLUE,
                fontName='Helvetica-Bold',
                spaceAfter=4
            )

            role_label = "You" if role == "user" else "Nova"
            story.append(Paragraph(role_label, role_style))

            # Message content
            content_style = ParagraphStyle(
                'Content',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                leftIndent=10
            )
            story.append(Paragraph(content.replace('\n', '<br/>'), content_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=12))

    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=GRAY,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
    story.append(Paragraph("<b>StarCiti Sales Agent</b> - Your AI-Powered Ship Consultant", footer_style))

    # Build PDF
    doc.build(story)
    return output_path


def generate_fleet_guide_pdf(
    conversation: Conversation,
    db: Session,
    output_path: Optional[str] = None
) -> str:
    """
    Generate fleet composition guide PDF with ship recommendations

    Args:
        conversation: Conversation object with recommended ships
        db: Database session for fetching ship details
        output_path: Optional custom output path

    Returns:
        Path to generated PDF file
    """
    if not output_path:
        filename = f"fleet_guide_{conversation.conversation_uuid}.pdf"
        output_path = str(OUTPUT_DIR / "fleet_guides" / filename)

    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=BLUE,
        spaceAfter=10,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=GRAY,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    # Cover page
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("Your Fleet Composition Guide", title_style))
    story.append(Paragraph("Personalized Ship Recommendations", subtitle_style))
    story.append(Spacer(1, 0.5*inch))

    cover_info_style = ParagraphStyle(
        'CoverInfo',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"<b>Prepared for:</b> {conversation.user_email or 'Prospective Citizen'}", cover_info_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated by <b>StarCiti Sales Agent</b><br/>{datetime.now().strftime('%B %d, %Y')}", cover_info_style))
    story.append(PageBreak())

    # Fetch ship details
    ships = []
    if conversation.recommended_ships:
        for ship_data in conversation.recommended_ships:
            ship_id = ship_data.get("id")
            if ship_id:
                ship = db.query(Ship).filter(Ship.id == ship_id).first()
                if ship:
                    ships.append({
                        "name": ship.name,
                        "manufacturer": ship.manufacturer_name or "Unknown",
                        "focus": ship.focus or "Multi-role",
                        "description": ship.description or "No description available",
                        "price_usd": f"${ship.price_usd:,.2f}" if ship.price_usd else "TBA",
                        "size": ship.size or "Unknown",
                        "crew_min": ship.crew_min or 0,
                        "crew_max": ship.crew_max or 0,
                        "cargo_capacity": ship.cargo_capacity or 0,
                        "max_speed": ship.max_speed or 0,
                        "recommendation_reason": ship_data.get("reason", "Recommended based on your preferences")
                    })

    # User preferences (extracted from conversation)
    user_preferences = _extract_preferences_from_transcript(conversation.conversation_transcript or [])

    # Preferences section
    story.append(Paragraph("Your Preferences", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))

    pref_data = [
        ["Budget:", user_preferences.get("budget", "Not specified")],
        ["Playstyle:", user_preferences.get("playstyle", "Not specified")],
        ["Crew Size:", user_preferences.get("crew_size", "Not specified")],
        ["Activities:", ", ".join(user_preferences.get("primary_activities", [])) or "Versatile gameplay"],
    ]

    pref_table = Table(pref_data, colWidths=[1.5*inch, 4.5*inch])
    pref_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(pref_table)
    story.append(Spacer(1, 0.3*inch))

    # Fleet analysis
    fleet_analysis = _generate_fleet_analysis(ships, user_preferences)
    story.append(Paragraph("Fleet Analysis", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(fleet_analysis, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Recommended ships
    story.append(PageBreak())
    story.append(Paragraph(f"Recommended Ships ({len(ships)})", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    for i, ship in enumerate(ships, 1):
        # Ship header
        ship_header_style = ParagraphStyle(
            'ShipHeader',
            parent=styles['Heading3'],
            fontSize=16,
            textColor=BLUE,
            spaceAfter=6
        )
        story.append(Paragraph(f"{i}. {ship['name']}", ship_header_style))

        mfr_style = ParagraphStyle(
            'Manufacturer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=GRAY,
            spaceAfter=10
        )
        story.append(Paragraph(f"{ship['manufacturer']} | {ship['focus']} | {ship['size']} Size | {ship['price_usd']}", mfr_style))

        # Description
        story.append(Paragraph(ship['description'], styles['Normal']))
        story.append(Spacer(1, 0.1*inch))

        # Recommendation reason
        reason_style = ParagraphStyle(
            'Reason',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=10,
            textColor=colors.HexColor("#1e3a8a"),
            spaceAfter=10
        )
        story.append(Paragraph(f"<b>Why this ship?</b> {ship['recommendation_reason']}", reason_style))

        # Specifications table
        spec_data = [
            ["Crew", "Cargo", "Max Speed"],
            [f"{ship['crew_min']}-{ship['crew_max']}", f"{ship['cargo_capacity']} SCU", f"{ship['max_speed']} m/s"]
        ]

        spec_table = Table(spec_data, colWidths=[2*inch, 2*inch, 2*inch])
        spec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), LIGHT_GRAY),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(spec_table)
        story.append(Spacer(1, 0.3*inch))

        if i < len(ships):
            story.append(HRFlowable(width="100%", thickness=1, color=GRAY, spaceAfter=20))

    # Next steps
    story.append(PageBreak())
    story.append(Paragraph("Next Steps", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    next_steps = _generate_next_steps(ships)
    for i, step in enumerate(next_steps, 1):
        story.append(Paragraph(f"{i}. {step}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))

    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=GRAY,
        alignment=TA_CENTER
    )
    story.append(Paragraph("<b>StarCiti Sales Agent</b> - Powered by Claude AI", footer_style))
    story.append(Paragraph("<i>Ship specifications and prices are subject to change during Star Citizen's development.</i>", footer_style))

    # Build PDF
    doc.build(story)
    return output_path


def _extract_preferences_from_transcript(transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract user preferences from conversation transcript"""
    preferences = {
        "budget": "Not specified",
        "playstyle": "Not specified",
        "crew_size": "Not specified",
        "primary_activities": []
    }

    # Simple keyword extraction
    full_text = " ".join([msg.get("content", "").lower() for msg in transcript if msg.get("role") == "user"])

    # Budget detection
    if "million" in full_text or "$" in full_text:
        if "100" in full_text:
            preferences["budget"] = "Under $100"
        elif "500" in full_text:
            preferences["budget"] = "$100-$500"
        else:
            preferences["budget"] = "Flexible"

    # Playstyle detection
    if "solo" in full_text or "alone" in full_text:
        preferences["playstyle"] = "Solo"
    elif "crew" in full_text or "friends" in full_text or "org" in full_text:
        preferences["playstyle"] = "Multi-crew"

    # Activities detection
    activities = []
    if "cargo" in full_text or "trading" in full_text or "hauling" in full_text:
        activities.append("Cargo/Trading")
    if "combat" in full_text or "fighting" in full_text or "bounty" in full_text:
        activities.append("Combat")
    if "exploration" in full_text or "explore" in full_text:
        activities.append("Exploration")
    if "mining" in full_text:
        activities.append("Mining")

    preferences["primary_activities"] = activities
    return preferences


def _generate_fleet_analysis(ships: List[Dict[str, Any]], preferences: Dict[str, Any]) -> str:
    """Generate fleet composition analysis"""
    if not ships:
        return "No ships recommended yet. Continue your conversation with Nova to get personalized recommendations!"

    analysis_parts = []

    # Fleet overview
    ship_names = ", ".join([s["name"] for s in ships])
    analysis_parts.append(f"Your recommended fleet consists of {len(ships)} ship{'s' if len(ships) > 1 else ''}: {ship_names}.")

    # Role coverage
    roles = set([s["focus"] for s in ships if s["focus"]])
    if len(roles) > 1:
        analysis_parts.append(f"This fleet provides versatility across {len(roles)} different roles, giving you flexibility in gameplay.")
    elif len(roles) == 1:
        analysis_parts.append(f"This focused fleet specializes in {list(roles)[0]}, perfect for dedicated operations.")

    # Crew requirements
    total_crew_max = sum([s["crew_max"] for s in ships if s["crew_max"]])
    solo_capable = [s for s in ships if s["crew_min"] <= 1]
    if solo_capable:
        analysis_parts.append(f"{len(solo_capable)} of these ships can be operated solo, ideal for independent gameplay.")
    if total_crew_max > 5:
        analysis_parts.append(f"For multi-crew operations, this fleet supports up to {total_crew_max} players simultaneously.")

    # Cargo capacity
    total_cargo = sum([s["cargo_capacity"] for s in ships if s["cargo_capacity"]])
    if total_cargo > 0:
        analysis_parts.append(f"Combined cargo capacity: {total_cargo:,} SCU for trading and logistics operations.")

    return " ".join(analysis_parts)


def _generate_next_steps(ships: List[Dict[str, Any]]) -> List[str]:
    """Generate actionable next steps"""
    steps = [
        "Visit the RSI Pledge Store (robertsspaceindustries.com/pledge/ships) to purchase these ships",
        "Join the Star Citizen community on Spectrum forums to connect with other players",
        "Watch ship review videos on YouTube to see these ships in action",
        "Consider starting with the most affordable ship and upgrading later"
    ]

    if ships:
        # Add ship-specific steps
        cheapest = min(ships, key=lambda s: float(s["price_usd"].replace("$", "").replace(",", "")) if s["price_usd"] != "TBA" else float('inf'))
        if cheapest["price_usd"] != "TBA":
            steps.insert(0, f"Start with the {cheapest['name']} ({cheapest['price_usd']}) as your entry ship")

    return steps


def generate_both_pdfs(
    conversation_id: int,
    db: Session
) -> Dict[str, str]:
    """
    Generate both transcript and fleet guide PDFs for a conversation

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
    transcript_path = generate_transcript_pdf(conversation)
    fleet_guide_path = generate_fleet_guide_pdf(conversation, db)

    # Update conversation with PDF paths
    conversation.transcript_pdf_path = transcript_path
    conversation.fleet_guide_pdf_path = fleet_guide_path
    db.commit()

    return {
        "transcript_pdf": transcript_path,
        "fleet_guide_pdf": fleet_guide_path
    }
