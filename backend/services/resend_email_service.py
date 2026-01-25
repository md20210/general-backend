"""
Resend Email Service for MVP Tax Spain Authentication
"""
import os
from typing import Optional
import httpx
from backend.config import settings


class ResendEmailService:
    """Service for sending emails via Resend API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RESEND_API_KEY", "re_hTZxVL5t_9CcWhbdQLNzCC6aJkd6bd1FW")
        self.from_email = "michael.dabrock@gmx.es"
        self.base_url = "https://api.resend.com"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email via Resend API

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            from_email: Sender email (optional, uses default if not provided)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": from_email or self.from_email,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content,
                    },
                )

                if response.status_code == 200:
                    return True
                else:
                    print(f"Failed to send email to {to_email}: {response.text}")
                    return False

        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_registration_email(
        self,
        to_email: str,
        vorname: str,
        nachname: str,
        verification_token: str
    ) -> bool:
        """
        Send registration confirmation email with verification link

        Args:
            to_email: User's email address
            vorname: User's first name
            nachname: User's last name
            verification_token: Email verification token

        Returns:
            bool: True if sent successfully
        """
        verification_url = f"https://www.dabrock.info/mvptaxspain/verify-email?token={verification_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #1e3a8a;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f3f4f6;
                    padding: 30px;
                    border-left: 1px solid #ddd;
                    border-right: 1px solid #ddd;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #1e3a8a;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #1f2937;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    border-radius: 0 0 5px 5px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MVP Tax Spain</h1>
            </div>
            <div class="content">
                <h2>Willkommen, {vorname} {nachname}!</h2>
                <p>Vielen Dank für Ihre Registrierung bei MVP Tax Spain.</p>
                <p>Bitte bestätigen Sie Ihre E-Mail-Adresse, indem Sie auf den folgenden Link klicken:</p>
                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">E-Mail bestätigen</a>
                </p>
                <p>Dieser Link ist 24 Stunden gültig.</p>
                <p>Falls Sie sich nicht registriert haben, können Sie diese E-Mail ignorieren.</p>
            </div>
            <div class="footer">
                <p>MVP Tax Spain - H7 Formular Service</p>
                <p>© 2026 All rights reserved</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=to_email,
            subject="Bestätigen Sie Ihre E-Mail-Adresse",
            html_content=html_content
        )

    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str
    ) -> bool:
        """
        Send password reset email with reset link

        Args:
            to_email: User's email address
            reset_token: Password reset token

        Returns:
            bool: True if sent successfully
        """
        reset_url = f"https://www.dabrock.info/mvptaxspain/reset-password?token={reset_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #1e3a8a;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f3f4f6;
                    padding: 30px;
                    border-left: 1px solid #ddd;
                    border-right: 1px solid #ddd;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #dc2626;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #1f2937;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    border-radius: 0 0 5px 5px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MVP Tax Spain</h1>
            </div>
            <div class="content">
                <h2>Passwort zurücksetzen</h2>
                <p>Sie haben eine Anfrage zum Zurücksetzen Ihres Passworts erhalten.</p>
                <p>Klicken Sie auf den folgenden Link, um ein neues Passwort zu setzen:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Passwort zurücksetzen</a>
                </p>
                <p>Dieser Link ist 1 Stunde gültig.</p>
                <p>Falls Sie diese Anfrage nicht gestellt haben, können Sie diese E-Mail ignorieren.</p>
            </div>
            <div class="footer">
                <p>MVP Tax Spain - H7 Formular Service</p>
                <p>© 2026 All rights reserved</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=to_email,
            subject="Passwort zurücksetzen",
            html_content=html_content
        )

    async def send_h7_export_copy(
        self,
        to_email: str,
        pdf_url: str
    ) -> bool:
        """
        Send H7 export copy email

        Args:
            to_email: User's email address
            pdf_url: URL to the exported PDF

        Returns:
            bool: True if sent successfully
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #1e3a8a;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f3f4f6;
                    padding: 30px;
                    border-left: 1px solid #ddd;
                    border-right: 1px solid #ddd;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #059669;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #1f2937;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    border-radius: 0 0 5px 5px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MVP Tax Spain</h1>
            </div>
            <div class="content">
                <h2>Ihr H7-Formular ist bereit!</h2>
                <p>Vielen Dank für die Nutzung von MVP Tax Spain.</p>
                <p>Ihr H7-Formular wurde erfolgreich erstellt und ist jetzt zum Download verfügbar:</p>
                <p style="text-align: center;">
                    <a href="{pdf_url}" class="button">PDF herunterladen</a>
                </p>
                <p>Das Dokument bleibt 30 Tage verfügbar.</p>
            </div>
            <div class="footer">
                <p>MVP Tax Spain - H7 Formular Service</p>
                <p>© 2026 All rights reserved</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=to_email,
            subject="Ihr H7-Formular ist bereit",
            html_content=html_content
        )


# Singleton instance
resend_email_service = ResendEmailService()
