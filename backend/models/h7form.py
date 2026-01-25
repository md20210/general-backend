"""H7 Form Data models for MVP Tax Spain."""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base


class H7FormData(Base):
    """H7 Form submission data with optional user association."""
    __tablename__ = "h7_form_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    email = Column(String(255), nullable=False, index=True)  # Always required (from user or manual)

    # Allgemeine Daten
    sendungsart = Column(String(100), nullable=True)
    warenwert_gesamt = Column(String(50), nullable=True)
    waehrung = Column(String(10), nullable=True)
    versandkosten = Column(String(50), nullable=True)
    gesamtbetrag_zoll = Column(String(50), nullable=True)
    art_lieferung = Column(String(100), nullable=True)

    # Absender
    absender_name = Column(String(255), nullable=True)
    absender_strasse = Column(String(255), nullable=True)
    absender_plz = Column(String(20), nullable=True)
    absender_ort = Column(String(100), nullable=True)
    absender_land = Column(String(100), nullable=True)
    absender_email = Column(String(255), nullable=True)
    absender_telefon = Column(String(50), nullable=True)

    # Empfänger
    empfaenger_name = Column(String(255), nullable=True)
    empfaenger_strasse = Column(String(255), nullable=True)
    empfaenger_plz = Column(String(20), nullable=True)
    empfaenger_ort = Column(String(100), nullable=True)
    empfaenger_insel = Column(String(100), nullable=True)
    empfaenger_nif = Column(String(50), nullable=True)
    empfaenger_email = Column(String(255), nullable=True)
    empfaenger_telefon = Column(String(50), nullable=True)

    # Warenpositionen (JSON array)
    warenpositionen = Column(JSON, nullable=True)

    # Export info
    exported_pdf_url = Column(String(500), nullable=True)
    wahrheitserklaerung = Column(String(10), nullable=True)  # "Ja" or null

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="h7_forms")

    def __repr__(self):
        return f"<H7FormData(id={self.id}, email={self.email}, user_id={self.user_id})>"


class AdminSettings(Base):
    """Admin settings for email configuration (singleton)."""
    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, default=1)

    # Email configuration
    email_sender = Column(String(255), nullable=False, default="michael.dabrock@gmx.es")
    resend_api_key = Column(String(500), nullable=True)  # Encrypted storage recommended

    # Feature flags
    email_verification_required = Column(String(10), default="Ja")  # Ja/Nein
    auto_logout_minutes = Column(Integer, default=30)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AdminSettings(email_sender={self.email_sender})>"


class PasswordResetToken(Base):
    """Password reset tokens with 1-hour expiration."""
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(String(10), default="Nein")  # Ja/Nein

    # Relationship
    user = relationship("User")

    def __repr__(self):
        return f"<PasswordResetToken(user_id={self.user_id}, used={self.used})>"


class EmailVerificationToken(Base):
    """Email verification tokens with 24-hour expiration."""
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(String(10), default="Nein")  # Ja/Nein

    # Relationship
    user = relationship("User")

    def __repr__(self):
        return f"<EmailVerificationToken(user_id={self.user_id}, used={self.used})>"
