"""
PDF Generator Service - Star Citizen Themed
Creates professional PDFs for conversation transcripts and fleet guides using ReportLab
Enhanced with Star Citizen branding and detailed ship specifications
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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from ..models.ship import Ship
from ..models.conversation import Conversation


# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "outputs"

# Ensure output directories exist
(OUTPUT_DIR / "transcripts").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "fleet_guides").mkdir(parents=True, exist_ok=True)

# Star Citizen Color Scheme
SC_BLUE = colors.HexColor("#00BFFF")  # Star Citizen bright blue
SC_DARK_BLUE = colors.HexColor("#1a2332")  # Dark navy background
SC_CYAN = colors.HexColor("#00D9FF")  # Bright cyan accents
SC_GOLD = colors.HexColor("#FFB600")  # Gold highlights
SC_GRAY = colors.HexColor("#8B9DB5")  # Light gray text
SC_LIGHT_BG = colors.HexColor("#243447")  # Light background panels
SC_WHITE = colors.HexColor("#FFFFFF")  # Pure white


def generate_transcript_pdf(
    conversation: Conversation,
    output_path: Optional[str] = None
) -> str:
    """
    Generate conversation transcript PDF using ReportLab with SC theme

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

    # Custom styles with SC theme
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=SC_CYAN,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=SC_GRAY,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    # Header with SC branding
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("STARCITI SALES AGENT", title_style))
    story.append(Paragraph("Conversation Transcript", subtitle_style))
    story.append(Spacer(1, 0.2*inch))

    # Meta information table with SC colors
    meta_data = [
        ["Conversation ID:", str(conversation.conversation_uuid)[:8].upper()],
        ["Started:", conversation.started_at.strftime("%B %d, %Y at %I:%M %p")],
        ["Completed:", conversation.completed_at.strftime("%B %d, %Y at %I:%M %p") if conversation.completed_at else "In Progress"],
        ["Contact:", conversation.user_email or "Not provided"],
    ]

    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), SC_LIGHT_BG),
        ('TEXTCOLOR', (0, 0), (0, -1), SC_CYAN),
        ('TEXTCOLOR', (1, 0), (1, -1), SC_WHITE),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, SC_BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4*inch))

    # Conversation messages with SC styling
    conversation_header = ParagraphStyle(
        'ConversationHeader',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=SC_CYAN,
        spaceAfter=20
    )
    story.append(Paragraph("CONVERSATION LOG", conversation_header))

    if conversation.transcript:
        for msg in conversation.transcript:
            role = msg.get("role", "")
            content = msg.get("content", "")

            # Role label with different colors for user/assistant
            role_style = ParagraphStyle(
                'Role',
                parent=styles['Normal'],
                fontSize=12,
                textColor=SC_GOLD if role == "user" else SC_CYAN,
                fontName='Helvetica-Bold',
                spaceAfter=4
            )

            role_label = "◆ CITIZEN" if role == "user" else "◆ NOVA"
            story.append(Paragraph(role_label, role_style))

            # Message content
            content_style = ParagraphStyle(
                'Content',
                parent=styles['Normal'],
                fontSize=10,
                textColor=SC_GRAY,
                spaceAfter=16,
                leftIndent=15
            )
            story.append(Paragraph(content.replace('\n', '<br/>'), content_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=SC_DARK_BLUE, spaceAfter=12))

    # Footer with SC branding
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=SC_GRAY,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
    story.append(Paragraph("<b>STARCITI SALES AGENT</b> - Powered by AI | See you in the 'verse", footer_style))

    # Build PDF
    doc.build(story)
    return output_path


def generate_fleet_guide_pdf(
    conversation: Conversation,
    db: Session,
    output_path: Optional[str] = None
) -> str:
    """
    Generate fleet composition guide PDF with detailed ship specifications

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

    # Custom styles with SC theme
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=32,
        textColor=SC_CYAN,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=SC_GOLD,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    # Cover page with SC branding
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("FLEET COMPOSITION GUIDE", title_style))
    story.append(Paragraph("◆ PERSONAL SHIP RECOMMENDATIONS ◆", subtitle_style))
    story.append(Spacer(1, 0.8*inch))

    cover_info_style = ParagraphStyle(
        'CoverInfo',
        parent=styles['Normal'],
        fontSize=12,
        textColor=SC_GRAY,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    citizen_name = conversation.user_name or conversation.user_email or "Prospective Citizen"
    story.append(Paragraph(f"<b>PREPARED FOR:</b> {citizen_name}", cover_info_style))
    story.append(Paragraph(f"<b>CLASSIFICATION:</b> CONFIDENTIAL", cover_info_style))
    story.append(Paragraph(f"<b>DATE:</b> {datetime.now().strftime('%B %d, %Y')}", cover_info_style))
    story.append(Paragraph(f"<b>AGENT ID:</b> {str(conversation.conversation_uuid)[:8].upper()}", cover_info_style))
    story.append(PageBreak())

    # Fetch detailed ship information from database
    ships = []
    if conversation.recommended_ships:
        for ship_data in conversation.recommended_ships:
            ship_id = ship_data.get("id")
            if ship_id:
                ship = db.query(Ship).filter(Ship.id == ship_id).first()
                if ship:
                    ships.append({
                        "ship_obj": ship,
                        "name": ship.name,
                        "manufacturer": ship.manufacturer.name if ship.manufacturer else "Unknown",
                        "focus": ship.focus or "Multi-role",
                        "description": ship.description or "No description available",
                        "recommendation_reason": ship_data.get("reason", "Recommended based on your preferences")
                    })

    # User preferences section
    user_preferences = _extract_preferences_from_transcript(conversation.transcript or [])

    pref_header_style = ParagraphStyle(
        'PrefHeader',
        parent=styles['Heading2'],
        fontSize=20,
        textColor=SC_CYAN,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph("◆ YOUR MISSION PROFILE", pref_header_style))

    pref_data = [
        ["PARAMETER", "VALUE"],
        ["Budget Range", user_preferences.get("budget", "Flexible")],
        ["Playstyle", user_preferences.get("playstyle", "Versatile")],
        ["Crew Preference", user_preferences.get("crew_size", "Any")],
        ["Primary Activities", ", ".join(user_preferences.get("primary_activities", ["General Operations"]))],
    ]

    pref_table = Table(pref_data, colWidths=[2.5*inch, 4*inch])
    pref_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SC_DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), SC_CYAN),
        ('BACKGROUND', (0, 1), (0, -1), SC_LIGHT_BG),
        ('TEXTCOLOR', (0, 1), (0, -1), SC_WHITE),
        ('TEXTCOLOR', (1, 1), (1, -1), SC_GOLD),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, SC_BLUE),
    ]))
    story.append(pref_table)
    story.append(Spacer(1, 0.3*inch))

    # Fleet analysis
    fleet_analysis = _generate_fleet_analysis(ships, user_preferences)
    analysis_style = ParagraphStyle(
        'Analysis',
        parent=styles['Normal'],
        fontSize=11,
        textColor=SC_GRAY,
        spaceAfter=20,
        alignment=TA_JUSTIFY
    )
    story.append(Paragraph("◆ FLEET STRATEGIC ANALYSIS", pref_header_style))
    story.append(Paragraph(fleet_analysis, analysis_style))

    # Recommended ships with full specifications
    story.append(PageBreak())
    story.append(Paragraph(f"◆ RECOMMENDED VESSELS ({len(ships)})", pref_header_style))
    story.append(Spacer(1, 0.2*inch))

    for i, ship_info in enumerate(ships, 1):
        ship = ship_info["ship_obj"]

        # Ship header with SC styling
        ship_header_style = ParagraphStyle(
            'ShipHeader',
            parent=styles['Heading3'],
            fontSize=18,
            textColor=SC_CYAN,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(f"[ {i} ] {ship_info['name'].upper()}", ship_header_style))

        # Manufacturer and class info
        mfr_style = ParagraphStyle(
            'Manufacturer',
            parent=styles['Normal'],
            fontSize=11,
            textColor=SC_GOLD,
            spaceAfter=12
        )
        manufacturer_line = f"{ship_info['manufacturer']} | {ship_info['focus']} | Type: {ship.type or 'Multi-Role'}"
        story.append(Paragraph(manufacturer_line, mfr_style))

        # Description
        desc_style = ParagraphStyle(
            'Description',
            parent=styles['Normal'],
            fontSize=10,
            textColor=SC_GRAY,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        )
        story.append(Paragraph(ship_info['description'], desc_style))

        # Recommendation reason with highlight
        reason_style = ParagraphStyle(
            'Reason',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=10,
            textColor=SC_CYAN,
            spaceAfter=15
        )
        story.append(Paragraph(f"<b>◆ WHY THIS VESSEL:</b> {ship_info['recommendation_reason']}", reason_style))

        # SPECIFICATIONS - Primary Stats
        spec_header_style = ParagraphStyle(
            'SpecHeader',
            parent=styles['Normal'],
            fontSize=12,
            textColor=SC_CYAN,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        story.append(Paragraph("TECHNICAL SPECIFICATIONS", spec_header_style))

        # Dimensions and Mass
        dim_data = [
            ["PARAMETER", "VALUE"],
            ["Length", f"{ship.length:.1f}m" if ship.length else "N/A"],
            ["Beam (Width)", f"{ship.beam:.1f}m" if ship.beam else "N/A"],
            ["Height", f"{ship.height:.1f}m" if ship.height else "N/A"],
            ["Mass", f"{ship.mass:,} kg" if ship.mass else "N/A"],
        ]

        dim_table = Table(dim_data, colWidths=[2.5*inch, 2*inch])
        dim_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SC_DARK_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), SC_CYAN),
            ('BACKGROUND', (0, 1), (0, -1), SC_LIGHT_BG),
            ('TEXTCOLOR', (0, 1), (0, -1), SC_WHITE),
            ('TEXTCOLOR', (1, 1), (1, -1), SC_GOLD),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, SC_BLUE),
        ]))
        story.append(dim_table)
        story.append(Spacer(1, 0.15*inch))

        # Performance Specs
        perf_data = [
            ["PARAMETER", "VALUE"],
            ["SCM Speed", f"{ship.speed_scm:.0f} m/s" if ship.speed_scm else "N/A"],
            ["Max Speed", f"{ship.speed_max:.0f} m/s" if ship.speed_max else "N/A"],
            ["0-SCM Accel", f"{ship.speed_zero_to_scm:.1f}s" if ship.speed_zero_to_scm else "N/A"],
            ["0-MAX Accel", f"{ship.speed_zero_to_max:.1f}s" if ship.speed_zero_to_max else "N/A"],
        ]

        perf_table = Table(perf_data, colWidths=[2.5*inch, 2*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SC_DARK_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), SC_CYAN),
            ('BACKGROUND', (0, 1), (0, -1), SC_LIGHT_BG),
            ('TEXTCOLOR', (0, 1), (0, -1), SC_WHITE),
            ('TEXTCOLOR', (1, 1), (1, -1), SC_GOLD),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, SC_BLUE),
        ]))
        story.append(perf_table)
        story.append(Spacer(1, 0.15*inch))

        # Operational Specs
        ops_data = [
            ["PARAMETER", "VALUE"],
            ["Crew (Min-Max)", f"{ship.crew_min or 1}-{ship.crew_max or ship.crew_min or 1}"],
            ["Cargo Capacity", f"{ship.cargo_capacity:,} SCU" if ship.cargo_capacity else "0 SCU"],
            ["Shield HP", f"{ship.shield_hp:,}" if ship.shield_hp else "N/A"],
            ["Quantum Range", f"{ship.quantum_range:,} Mm" if ship.quantum_range else "N/A"],
            ["Fuel Capacity", f"{ship.fuel_capacity:,} L" if ship.fuel_capacity else "N/A"],
        ]

        ops_table = Table(ops_data, colWidths=[2.5*inch, 2*inch])
        ops_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SC_DARK_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), SC_CYAN),
            ('BACKGROUND', (0, 1), (0, -1), SC_LIGHT_BG),
            ('TEXTCOLOR', (0, 1), (0, -1), SC_WHITE),
            ('TEXTCOLOR', (1, 1), (1, -1), SC_GOLD),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, SC_BLUE),
        ]))
        story.append(ops_table)
        story.append(Spacer(1, 0.3*inch))

        # Separator between ships
        if i < len(ships):
            story.append(HRFlowable(width="100%", thickness=2, color=SC_BLUE, spaceAfter=25))

    # Next steps
    story.append(PageBreak())
    story.append(Paragraph("◆ MISSION DIRECTIVES", pref_header_style))
    story.append(Spacer(1, 0.2*inch))

    next_steps = _generate_next_steps(ships)
    for i, step in enumerate(next_steps, 1):
        step_style = ParagraphStyle(
            'Step',
            parent=styles['Normal'],
            fontSize=11,
            textColor=SC_GRAY,
            spaceAfter=10,
            leftIndent=20
        )
        story.append(Paragraph(f"<b>{i}.</b> {step}", step_style))

    # Footer with SC branding
    story.append(Spacer(1, inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=SC_GRAY,
        alignment=TA_CENTER,
        spaceAfter=5
    )
    story.append(Paragraph("<b>STARCITI SALES AGENT</b> - Powered by Claude AI", footer_style))
    story.append(Paragraph("◆ See you in the 'verse ◆", footer_style))
    story.append(Paragraph("<i>Ship specifications and prices subject to change during Star Citizen development.</i>", footer_style))
    story.append(Paragraph("<i>Always verify current information at robertsspaceindustries.com before purchasing.</i>", footer_style))

    # Build PDF
    doc.build(story)
    return output_path


def _extract_preferences_from_transcript(transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract user preferences from conversation transcript"""
    preferences = {
        "budget": "Flexible",
        "playstyle": "Versatile",
        "crew_size": "Any",
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
        preferences["playstyle"] = "Solo Operations"
    elif "crew" in full_text or "friends" in full_text or "org" in full_text:
        preferences["playstyle"] = "Multi-Crew Operations"

    # Activities detection
    activities = []
    if "cargo" in full_text or "trading" in full_text or "hauling" in full_text:
        activities.append("Cargo & Trading")
    if "combat" in full_text or "fighting" in full_text or "bounty" in full_text:
        activities.append("Combat Operations")
    if "exploration" in full_text or "explore" in full_text:
        activities.append("Exploration")
    if "mining" in full_text:
        activities.append("Mining")

    if not activities:
        activities = ["General Operations"]

    preferences["primary_activities"] = activities
    return preferences


def _generate_fleet_analysis(ships: List[Dict[str, Any]], preferences: Dict[str, Any]) -> str:
    """Generate comprehensive fleet composition analysis"""
    if not ships:
        return "No vessels have been recommended at this time. Please continue your consultation with Nova to receive personalized ship recommendations."

    analysis_parts = []

    # Fleet overview
    ship_names = ", ".join([s["name"] for s in ships])
    analysis_parts.append(f"Your recommended fleet comprises {len(ships)} vessel{'s' if len(ships) > 1 else ''}: {ship_names}.")

    # Role coverage analysis
    roles = list(set([s["focus"] for s in ships if s["focus"]]))
    if len(roles) > 2:
        analysis_parts.append(f"This diverse fleet provides operational flexibility across {len(roles)} different mission profiles: {', '.join(roles)}. This versatility allows you to adapt to various gameplay scenarios and economic opportunities in the 'verse.")
    elif len(roles) == 2:
        analysis_parts.append(f"This balanced fleet specializes in {roles[0]} and {roles[1]}, providing focused capability while maintaining operational flexibility.")
    elif len(roles) == 1:
        analysis_parts.append(f"This specialized fleet is optimized for {roles[0]} operations, perfect for dedicated mission execution and mastery of this role.")

    # Crew requirements analysis
    ship_objs = [s["ship_obj"] for s in ships]
    total_crew_max = sum([s.crew_max for s in ship_objs if s.crew_max])
    solo_capable = [s for s in ship_objs if (s.crew_min or 1) <= 1]

    if solo_capable:
        analysis_parts.append(f"{len(solo_capable)} of these vessels can be operated solo, making them ideal for independent citizens and flexible deployment scenarios.")
    if total_crew_max > 5:
        analysis_parts.append(f"When fully crewed, this fleet supports up to {total_crew_max} personnel simultaneously, excellent for organization-level operations and multi-crew gameplay.")

    # Cargo capacity analysis
    total_cargo = sum([s.cargo_capacity for s in ship_objs if s.cargo_capacity])
    if total_cargo > 100:
        analysis_parts.append(f"Combined cargo capacity totals {total_cargo:,} SCU, providing substantial logistics capability for trading operations and resource hauling.")
    elif total_cargo > 0:
        analysis_parts.append(f"This fleet includes {total_cargo:,} SCU of cargo capacity for basic trading and resource transport needs.")

    return " ".join(analysis_parts)


def _generate_next_steps(ships: List[Dict[str, Any]]) -> List[str]:
    """Generate actionable next steps for citizens"""
    steps = [
        "Visit the RSI Pledge Store at robertsspaceindustries.com/pledge/ships to review and purchase these vessels",
        "Join the Star Citizen community on Spectrum forums to connect with other citizens and organizations",
        "Watch ship review videos and gameplay footage on YouTube to see these vessels in operational scenarios",
        "Download and install Star Citizen to begin your journey (robertsspaceindustries.com/download)",
        "Consider joining an organization to maximize multi-crew opportunities and fleet synergies",
    ]

    if ships:
        # Add ship-specific recommendations
        ship_objs = [s["ship_obj"] for s in ships]

        # Find starter ship recommendation
        solo_ships = [s for s in ship_objs if (s.crew_min or 1) <= 1]
        if solo_ships:
            cheapest_solo = solo_ships[0]  # Would need price comparison
            steps.insert(0, f"Begin your career with a solo-capable vessel like the {cheapest_solo.name} to learn game mechanics independently")

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
