"""
SMTP Email Service for MVP Tax Spain
Supports Gmail, GMX, and other SMTP providers
"""
import smtplib
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from functools import partial

logger = logging.getLogger(__name__)

# Ensure logger outputs to console
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class SMTPEmailService:
    """Service for sending emails via SMTP"""

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        # GMX SMTP settings (default)
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "mail.gmx.net")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "michael.dabrock@gmx.es")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.from_email = from_email or os.getenv("SMTP_FROM_EMAIL", "michael.dabrock@gmx.es")

        logger.info(f"🔧 SMTP Email Service initialized")
        logger.info(f"   Host: {self.smtp_host}:{self.smtp_port}")
        logger.info(f"   User: {self.smtp_user}")
        logger.info(f"   From: {self.from_email}")
        logger.info(f"   Password set: {'Yes' if self.smtp_password else 'No'}")

    def _send_email_sync(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Synchronous email sending (to be called from async context)
        """
        try:
            logger.info(f"📧 Attempting to send email to {to_email}")
            logger.info(f"   SMTP: {self.smtp_host}:{self.smtp_port}")
            logger.info(f"   User: {self.smtp_user}")

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or self.from_email
            msg['To'] = to_email

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Connect to SMTP server
            logger.info(f"   Connecting to SMTP server...")
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
            logger.info(f"   Starting TLS...")
            server.starttls()
            logger.info(f"   Logging in...")
            server.login(self.smtp_user, self.smtp_password)
            logger.info(f"   Sending message...")
            server.send_message(msg)
            server.quit()

            logger.info(f"✅ Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Authentication failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False
        except Exception as e:
            error_msg = f"Failed to send email to {to_email}: {type(e).__name__}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP (async wrapper)

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            from_email: Sender email (optional, uses default if not provided)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        # Run synchronous SMTP in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(self._send_email_sync, to_email, subject, html_content, from_email)
        )

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
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    border: 1px solid #ddd;
                }}
                .header {{
                    background-color: #2563eb;
                    color: white;
                    padding: 20px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #2563eb;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background-color: #1d4ed8;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🇪🇸 MVP Tax Spain</h1>
                    <p>Willkommen bei der Steuerfallverwaltung</p>
                </div>
                <div class="content">
                    <h2>Hallo {vorname} {nachname}!</h2>
                    <p>Vielen Dank für Ihre Registrierung bei MVP Tax Spain.</p>
                    <p>Bitte bestätigen Sie Ihre E-Mail-Adresse, indem Sie auf den folgenden Button klicken:</p>
                    
                    <center>
                        <a href="{verification_url}" class="button">
                            E-Mail-Adresse bestätigen
                        </a>
                    </center>
                    
                    <p>Oder kopieren Sie diesen Link in Ihren Browser:</p>
                    <p style="word-break: break-all; color: #2563eb;">{verification_url}</p>
                    
                    <p><strong>Wichtig:</strong> Dieser Link ist 24 Stunden gültig.</p>
                </div>
                <div class="footer">
                    <p>Diese E-Mail wurde automatisch generiert. Bitte antworten Sie nicht darauf.</p>
                    <p>&copy; 2026 MVP Tax Spain - Steuerfallverwaltung</p>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=to_email,
            subject="MVP Tax Spain - E-Mail-Adresse bestätigen",
            html_content=html_content
        )

    async def send_password_reset_email(
        self,
        to_email: str,
        vorname: str,
        nachname: str,
        reset_token: str
    ) -> bool:
        """
        Send password reset email with reset link

        Args:
            to_email: User's email address
            vorname: User's first name
            nachname: User's last name
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
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    border: 1px solid #ddd;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #dc2626;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🔐 Passwort zurücksetzen</h2>
                <p>Hallo {vorname} {nachname},</p>
                <p>Sie haben eine Anfrage zum Zurücksetzen Ihres Passworts gestellt.</p>
                
                <center>
                    <a href="{reset_url}" class="button">
                        Passwort zurücksetzen
                    </a>
                </center>
                
                <p>Oder kopieren Sie diesen Link: {reset_url}</p>
                <p><strong>Hinweis:</strong> Dieser Link ist 1 Stunde gültig.</p>
                <p>Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail.</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=to_email,
            subject="MVP Tax Spain - Passwort zurücksetzen",
            html_content=html_content
        )


# Create singleton instance
smtp_email_service = SMTPEmailService()
