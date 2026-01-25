"""H7 Form and Auth Pydantic schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Warenposition Schema
class WarenpositionSchema(BaseModel):
    """Schema for a single goods position."""
    beschreibung: Optional[str] = None
    menge: Optional[str] = None
    einzelpreis: Optional[str] = None
    gesamtpreis: Optional[str] = None
    ursprungsland: Optional[str] = None
    zolltarifnummer: Optional[str] = None


# H7 Form Schemas
class H7FormDataCreate(BaseModel):
    """Schema for creating H7 form data."""
    email: EmailStr  # Required

    # Allgemeine Daten
    sendungsart: Optional[str] = None
    warenwert_gesamt: Optional[str] = None
    waehrung: Optional[str] = None
    versandkosten: Optional[str] = None
    gesamtbetrag_zoll: Optional[str] = None
    art_lieferung: Optional[str] = None

    # Absender
    absender_name: Optional[str] = None
    absender_strasse: Optional[str] = None
    absender_plz: Optional[str] = None
    absender_ort: Optional[str] = None
    absender_land: Optional[str] = None
    absender_email: Optional[str] = None
    absender_telefon: Optional[str] = None

    # Empfänger
    empfaenger_name: Optional[str] = None
    empfaenger_strasse: Optional[str] = None
    empfaenger_plz: Optional[str] = None
    empfaenger_ort: Optional[str] = None
    empfaenger_insel: Optional[str] = None
    empfaenger_nif: Optional[str] = None
    empfaenger_email: Optional[str] = None
    empfaenger_telefon: Optional[str] = None

    # Warenpositionen
    warenpositionen: Optional[List[Dict[str, Any]]] = None

    # Export info
    exported_pdf_url: Optional[str] = None
    wahrheitserklaerung: Optional[str] = None


class H7FormDataRead(BaseModel):
    """Schema for reading H7 form data."""
    id: int
    user_id: Optional[UUID] = None
    email: str

    # Allgemeine Daten
    sendungsart: Optional[str] = None
    warenwert_gesamt: Optional[str] = None
    waehrung: Optional[str] = None
    versandkosten: Optional[str] = None
    gesamtbetrag_zoll: Optional[str] = None
    art_lieferung: Optional[str] = None

    # Absender
    absender_name: Optional[str] = None
    absender_strasse: Optional[str] = None
    absender_plz: Optional[str] = None
    absender_ort: Optional[str] = None
    absender_land: Optional[str] = None
    absender_email: Optional[str] = None
    absender_telefon: Optional[str] = None

    # Empfänger
    empfaenger_name: Optional[str] = None
    empfaenger_strasse: Optional[str] = None
    empfaenger_plz: Optional[str] = None
    empfaenger_ort: Optional[str] = None
    empfaenger_insel: Optional[str] = None
    empfaenger_nif: Optional[str] = None
    empfaenger_email: Optional[str] = None
    empfaenger_telefon: Optional[str] = None

    # Warenpositionen
    warenpositionen: Optional[List[Dict[str, Any]]] = None

    # Export info
    exported_pdf_url: Optional[str] = None
    wahrheitserklaerung: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Admin Settings Schemas
class AdminSettingsRead(BaseModel):
    """Schema for reading admin settings."""
    id: int
    email_sender: str
    email_verification_required: str
    auto_logout_minutes: int
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminSettingsUpdate(BaseModel):
    """Schema for updating admin settings."""
    email_sender: Optional[str] = None
    resend_api_key: Optional[str] = None
    email_verification_required: Optional[str] = None
    auto_logout_minutes: Optional[int] = None


# Auth Schemas
class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset."""
    token: str
    new_password: str


class UserRegisterExtended(BaseModel):
    """Extended registration schema with profile fields."""
    email: EmailStr
    password: str
    vorname: str
    nachname: str
    sprache: str = "de"
    telefonnummer: Optional[str] = None
