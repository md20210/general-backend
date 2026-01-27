"""H7 Form Data models for MVP Tax Spain."""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean, Numeric, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base
import uuid


class H7FormData(Base):
    """H7 Form submission data with optional user association - Main table."""
    __tablename__ = "h7_form_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    email = Column(String(255), nullable=False, index=True)  # Always required (from user or manual)

    # Workflow Type (NEW)
    workflow = Column(String(10), nullable=True)  # 'B2C' oder 'C2C'

    # Allgemeine Daten - ERWEITERT
    sendungsart = Column(String(100), nullable=True)
    warenwert_gesamt = Column(Numeric(10, 2), nullable=True)  # Changed to Numeric
    waehrung = Column(String(10), default='EUR')
    versandkosten = Column(Numeric(10, 2), nullable=True)  # Changed to Numeric
    versicherungskosten = Column(Numeric(10, 2), nullable=True)  # NEW
    gesamtbetrag_zoll = Column(Numeric(10, 2), nullable=True)  # Changed to Numeric
    art_lieferung = Column(String(100), nullable=True)  # 'Kauf' oder 'Geschenk'

    # Absender - mit ISO Code
    absender_name = Column(String(255), nullable=True)
    absender_strasse = Column(String(255), nullable=True)
    absender_plz = Column(String(20), nullable=True)
    absender_ort = Column(String(100), nullable=True)
    absender_land = Column(String(100), nullable=True)  # Full name
    absender_land_iso = Column(String(2), nullable=True)  # NEW: ISO code
    absender_email = Column(String(255), nullable=True)
    absender_telefon = Column(String(50), nullable=True)

    # Empfänger - mit ISO code entfernt (immer Spanien/Kanaren)
    empfaenger_name = Column(String(255), nullable=True)
    empfaenger_strasse = Column(String(255), nullable=True)
    empfaenger_plz = Column(String(20), nullable=True)
    empfaenger_ort = Column(String(100), nullable=True)
    empfaenger_insel = Column(String(100), nullable=True)
    empfaenger_nif = Column(String(50), nullable=True)
    empfaenger_email = Column(String(255), nullable=True)
    empfaenger_telefon = Column(String(50), nullable=True)

    # Warenpositionen (JSON array) - bleibt JSON für Flexibilität
    warenpositionen = Column(JSON, nullable=True)

    # Rechnung/Wertnachweis - ERWEITERT
    rechnungsnummer = Column(String(100), nullable=True)  # B2C
    rechnungsdatum = Column(Date, nullable=True)  # B2C
    rechnung_hochgeladen = Column(Boolean, default=False)  # B2C
    mwst_ausgewiesen = Column(Boolean, default=False)  # B2C
    mwst_warnung_akzeptiert = Column(Boolean, default=False)  # B2C
    wertangabe_versender = Column(Numeric(10, 2), nullable=True)  # C2C
    keine_rechnung_vorhanden = Column(Boolean, default=False)  # C2C
    schaetzung_geschenk = Column(Numeric(10, 2), nullable=True)  # C2C
    zahlungsnachweis_file_path = Column(String(500), nullable=True)  # B2C

    # Zusatzinformationen - ERWEITERT
    wahrheitserklaerung = Column(Boolean, default=False)  # Changed to Boolean
    bemerkungen = Column(Text, nullable=True)  # NEW

    # Export info
    exported_pdf_url = Column(String(500), nullable=True)

    # Status tracking
    status = Column(String(50), default='draft')  # draft, submitted, processing, completed, error
    validation_errors = Column(JSON, nullable=True)  # Store validation errors

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="h7_forms")
    goods_positions = relationship("GoodsPosition", back_populates="h7_form", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<H7FormData(id={self.id}, email={self.email}, workflow={self.workflow}, status={self.status})>"


class GoodsPosition(Base):
    """Individual goods position - separate table for proper normalization."""
    __tablename__ = "goods_positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    h7_form_id = Column(Integer, ForeignKey("h7_form_data.id", ondelete="CASCADE"), nullable=False, index=True)

    position_nr = Column(Integer, nullable=False)  # Sequential number

    # Description
    warenbeschreibung = Column(String(500), nullable=False)
    warenbeschreibung_es = Column(String(500), nullable=True)  # Spanish translation

    # Quantities and prices
    anzahl = Column(Integer, nullable=False)  # >= 1
    stueckpreis = Column(Numeric(10, 2), nullable=False)  # >= 0.01
    gesamtwert = Column(Numeric(10, 2), nullable=False)  # Calculated

    # Origin and classification
    ursprungsland_iso = Column(String(2), nullable=False)
    zolltarifnummer = Column(String(10), nullable=True)  # Optional but recommended

    # Additional info
    gewicht = Column(Numeric(10, 2), nullable=True)  # Gross or net weight
    zustand = Column(String(20), nullable=True)  # 'Neu' oder 'Gebraucht'

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    h7_form = relationship("H7FormData", back_populates="goods_positions")

    def __repr__(self):
        return f"<GoodsPosition(id={self.id}, position_nr={self.position_nr}, description={self.warenbeschreibung[:30]})>"


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
