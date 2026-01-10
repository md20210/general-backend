"""
Email service for sending newsletters
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import os


class EmailService:
    """Service for sending emails via SMTP"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "mail.gmx.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "michael.dabrock@gmx.es")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "michael.dabrock@gmx.es")
        self.from_name = os.getenv("FROM_NAME", "Bar Ca l'Elena")

    def create_newsletter_html(
        self,
        subject: str,
        content: str,
        language: str
    ) -> str:
        """
        Create HTML email template for newsletter

        Args:
            subject: Newsletter subject
            content: Newsletter content
            language: Language code (ca, es, en, de, fr)

        Returns:
            HTML string
        """
        # Get unsubscribe text in the appropriate language
        unsubscribe_texts = {
            "ca": "Si no vols rebre més correus, pots donar-te de baixa aquí",
            "es": "Si no deseas recibir más correos, puedes darte de baja aquí",
            "en": "If you no longer wish to receive emails, you can unsubscribe here",
            "de": "Wenn Sie keine E-Mails mehr erhalten möchten, können Sie sich hier abmelden",
            "fr": "Si vous ne souhaitez plus recevoir d'e-mails, vous pouvez vous désabonner ici"
        }

        unsubscribe_text = unsubscribe_texts.get(language, unsubscribe_texts["ca"])

        html = f"""
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
                    background-color: #8B4513;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #FFF8E1;
                    padding: 30px;
                    border-left: 1px solid #ddd;
                    border-right: 1px solid #ddd;
                }}
                .footer {{
                    background-color: #3E2723;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    border-radius: 0 0 5px 5px;
                }}
                .footer a {{
                    color: #D2691E;
                    text-decoration: none;
                }}
                h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content-text {{
                    white-space: pre-wrap;
                    color: #3E2723;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Bar Ca l'Elena</h1>
            </div>
            <div class="content">
                <h2 style="color: #8B4513;">{subject}</h2>
                <div class="content-text">{content}</div>
            </div>
            <div class="footer">
                <p>Bar Ca l'Elena</p>
                <p>Carrer d'Amadeu Torner, 20<br>
                08902 L'Hospitalet de Llobregat, Barcelona</p>
                <p>📞 +34 933 36 50 43</p>
                <p style="margin-top: 20px;">
                    <a href="https://www.dabrock.info/morningbar/unsubscribe?email={{{{email}}}}">{unsubscribe_text}</a>
                </p>
            </div>
        </body>
        </html>
        """
        return html

    def send_newsletter(
        self,
        to_email: str,
        to_name: str,
        subject_translations: Dict[str, str],
        content_translations: Dict[str, str],
        language: str = "ca"
    ) -> bool:
        """
        Send newsletter email to a subscriber

        Args:
            to_email: Recipient email address
            to_name: Recipient name (optional)
            subject_translations: Dict with subject in all languages
            content_translations: Dict with content in all languages
            language: Recipient's preferred language

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Get subject and content in recipient's language
            subject = subject_translations.get(language, subject_translations.get("ca", ""))
            content = content_translations.get(language, content_translations.get("ca", ""))

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = f"{to_name} <{to_email}>" if to_name else to_email

            # Create HTML body
            html_body = self.create_newsletter_html(subject, content, language)
            html_part = MIMEText(html_body, "html", "utf-8")

            # Create plain text version (fallback)
            text_body = f"{subject}\n\n{content}\n\n---\nBar Ca l'Elena\nCarrer d'Amadeu Torner, 20\n08902 L'Hospitalet de Llobregat, Barcelona\n+34 933 36 50 43"
            text_part = MIMEText(text_body, "plain", "utf-8")

            # Attach parts (text first, then HTML for better client support)
            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_newsletter_batch(
        self,
        subscribers: List[tuple],
        subject_translations: Dict[str, str],
        content_translations: Dict[str, str]
    ) -> Dict[str, int]:
        """
        Send newsletter to multiple subscribers

        Args:
            subscribers: List of tuples (email, name, language)
            subject_translations: Dict with subject in all languages
            content_translations: Dict with content in all languages

        Returns:
            Dict with success and failure counts
        """
        success_count = 0
        failure_count = 0

        for email, name, language in subscribers:
            success = self.send_newsletter(
                to_email=email,
                to_name=name or "",
                subject_translations=subject_translations,
                content_translations=content_translations,
                language=language or "ca"
            )

            if success:
                success_count += 1
            else:
                failure_count += 1

        return {
            "success": success_count,
            "failed": failure_count,
            "total": success_count + failure_count
        }


# Singleton instance
email_service = EmailService()
