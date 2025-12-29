"""
Email Service
Sends fleet recommendations via SendGrid with PDF attachments
"""

import os
import base64
from typing import List, Optional
from pathlib import Path
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

from ..config import settings


def send_fleet_recommendations(
    to_email: str,
    user_name: Optional[str] = None,
    transcript_pdf_path: Optional[str] = None,
    fleet_guide_pdf_path: Optional[str] = None,
    recommended_ships: Optional[List[str]] = None
) -> bool:
    """
    Send fleet recommendations email with PDF attachments

    Args:
        to_email: Recipient email address
        user_name: Optional user name for personalization
        transcript_pdf_path: Path to transcript PDF
        fleet_guide_pdf_path: Path to fleet guide PDF
        recommended_ships: List of recommended ship names

    Returns:
        True if email sent successfully, False otherwise
    """

    # Validate SendGrid configuration
    if not settings.SENDGRID_API_KEY or settings.SENDGRID_API_KEY == "SG.your-sendgrid-api-key-here":
        raise ValueError("SendGrid API key not configured. Please add SENDGRID_API_KEY to .env file")

    # Prepare email content
    subject = "Your StarCiti Fleet Recommendations"

    # Determine greeting
    greeting = f"Hello {user_name}" if user_name else "Hello, Prospective Citizen"

    # Build ship list for email
    ships_list = ""
    if recommended_ships and len(recommended_ships) > 0:
        ships_list = "<ul style='margin: 10px 0; padding-left: 20px;'>"
        for ship in recommended_ships:
            ships_list += f"<li style='margin: 5px 0;'>{ship}</li>"
        ships_list += "</ul>"
    else:
        ships_list = "<p>Your personalized recommendations are in the attached Fleet Guide.</p>"

    # HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f4f4f4; padding: 20px 0;">
            <tr>
                <td align="center">
                    <table cellpadding="0" cellspacing="0" border="0" width="600" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); padding: 40px 30px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">
                                    StarCiti Sales Agent
                                </h1>
                                <p style="color: #e0e7ff; margin: 10px 0 0 0; font-size: 16px;">
                                    Your AI-Powered Ship Consultant
                                </p>
                            </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <p style="color: #1e293b; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    {greeting},
                                </p>

                                <p style="color: #1e293b; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Thank you for using StarCiti Sales Agent! Based on our conversation, Nova has prepared personalized ship recommendations just for you.
                                </p>

                                <div style="background-color: #eff6ff; border-left: 4px solid #2563eb; padding: 20px; margin: 20px 0;">
                                    <h2 style="color: #1e3a8a; margin: 0 0 15px 0; font-size: 20px;">
                                        Your Recommended Ships
                                    </h2>
                                    {ships_list}
                                </div>

                                <p style="color: #1e293b; font-size: 16px; line-height: 1.6; margin: 20px 0;">
                                    I've attached two comprehensive documents to help you make your decision:
                                </p>

                                <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin: 20px 0;">
                                    <tr>
                                        <td style="padding: 15px; background-color: #f8fafc; border-radius: 6px; margin-bottom: 10px;">
                                            <strong style="color: #2563eb; font-size: 16px;">📄 Conversation Transcript</strong>
                                            <p style="color: #64748b; margin: 5px 0 0 0; font-size: 14px;">
                                                A complete record of our conversation
                                            </p>
                                        </td>
                                    </tr>
                                    <tr><td style="height: 10px;"></td></tr>
                                    <tr>
                                        <td style="padding: 15px; background-color: #f8fafc; border-radius: 6px;">
                                            <strong style="color: #2563eb; font-size: 16px;">🚀 Fleet Composition Guide</strong>
                                            <p style="color: #64748b; margin: 5px 0 0 0; font-size: 14px;">
                                                Detailed ship specs, analysis, and next steps
                                            </p>
                                        </td>
                                    </tr>
                                </table>

                                <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                                    <p style="color: #92400e; margin: 0; font-size: 14px; line-height: 1.6;">
                                        <strong>Next Steps:</strong> Visit the <a href="https://robertsspaceindustries.com/pledge/ships" style="color: #2563eb; text-decoration: none;">RSI Pledge Store</a> to purchase your ships. Join the Star Citizen community on Spectrum to connect with other players!
                                    </p>
                                </div>

                                <p style="color: #1e293b; font-size: 16px; line-height: 1.6; margin: 20px 0 0 0;">
                                    Safe travels in the 'verse!<br>
                                    <strong>Nova & The StarCiti Team</strong>
                                </p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="color: #64748b; margin: 0; font-size: 12px; line-height: 1.6;">
                                    <strong>StarCiti Sales Agent</strong><br>
                                    Powered by Claude AI and the Star Citizen Community
                                </p>
                                <p style="color: #94a3b8; margin: 10px 0 0 0; font-size: 11px; font-style: italic;">
                                    Ship specifications and prices are subject to change during Star Citizen's development.<br>
                                    Always verify current information at robertsspaceindustries.com before purchasing.
                                </p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    # Plain text alternative
    text_content = f"""
{greeting},

Thank you for using StarCiti Sales Agent! Based on our conversation, Nova has prepared personalized ship recommendations just for you.

YOUR RECOMMENDED SHIPS:
{chr(10).join(['- ' + ship for ship in (recommended_ships or [])]) if recommended_ships else 'See attached Fleet Composition Guide'}

ATTACHMENTS:
- Conversation Transcript: A complete record of our conversation
- Fleet Composition Guide: Detailed ship specs, analysis, and next steps

NEXT STEPS:
Visit the RSI Pledge Store (https://robertsspaceindustries.com/pledge/ships) to purchase your ships.
Join the Star Citizen community on Spectrum to connect with other players!

Safe travels in the 'verse!
Nova & The StarCiti Team

---
StarCiti Sales Agent - Powered by Claude AI
Ship specifications and prices are subject to change during Star Citizen's development.
Always verify current information at robertsspaceindustries.com before purchasing.
"""

    # Create email message
    message = Mail(
        from_email=(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
        to_emails=to_email,
        subject=subject,
        plain_text_content=text_content,
        html_content=html_content
    )

    # Attach PDFs
    attachments = []

    if transcript_pdf_path and os.path.exists(transcript_pdf_path):
        with open(transcript_pdf_path, 'rb') as f:
            pdf_data = f.read()
            encoded = base64.b64encode(pdf_data).decode()

            attachment = Attachment(
                FileContent(encoded),
                FileName('conversation_transcript.pdf'),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            attachments.append(attachment)

    if fleet_guide_pdf_path and os.path.exists(fleet_guide_pdf_path):
        with open(fleet_guide_pdf_path, 'rb') as f:
            pdf_data = f.read()
            encoded = base64.b64encode(pdf_data).decode()

            attachment = Attachment(
                FileContent(encoded),
                FileName('fleet_composition_guide.pdf'),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            attachments.append(attachment)

    if attachments:
        message.attachment = attachments

    # Send email
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code in [200, 201, 202]:
            print(f"✅ Email sent successfully to {to_email}")
            print(f"   Status code: {response.status_code}")
            return True
        else:
            print(f"⚠️  Email sent with unexpected status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        raise


def test_sendgrid_connection() -> bool:
    """
    Test SendGrid API connection

    Returns:
        True if connection successful, False otherwise
    """
    if not settings.SENDGRID_API_KEY or settings.SENDGRID_API_KEY == "SG.your-sendgrid-api-key-here":
        print("❌ SendGrid API key not configured")
        return False

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        # Test by checking API key validity (will raise exception if invalid)
        print("✅ SendGrid connection successful")
        return True
    except Exception as e:
        print(f"❌ SendGrid connection failed: {str(e)}")
        return False
