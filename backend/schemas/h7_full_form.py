"""Pydantic schemas for full H7 form implementation."""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Literal
from datetime import date
from decimal import Decimal


# ============================================================================
# SECTION 1: GENERAL DATA SCHEMAS
# ============================================================================

class GeneralDataSchema(BaseModel):
    """Section 1: Allgemeine Sendungsdaten"""
    workflow: Literal['B2C', 'C2C'] = Field(..., description="Type of workflow")
    sendungsart: Optional[str] = Field(None, max_length=100)
    warenwert_gesamt: Decimal = Field(..., ge=0.01, le=150.00, description="Must be <= €150")
    waehrung: str = Field(default="EUR", max_length=10)
    versandkosten: Decimal = Field(..., ge=0, description="Shipping costs, explicitly 0 if zero")
    versicherungskosten: Optional[Decimal] = Field(None, ge=0)
    gesamtbetrag_zoll: Optional[Decimal] = Field(None, ge=0, description="Calculated total")
    art_lieferung: Literal['Kauf', 'Geschenk'] = Field(..., description="Purchase or Gift")


# ============================================================================
# SECTION 2: SENDER DATA SCHEMAS
# ============================================================================

class SenderDataSchema(BaseModel):
    """Section 2: Absenderdaten"""
    name_firma: str = Field(..., min_length=1, max_length=255)
    strasse_hausnummer: str = Field(..., max_length=255)
    postleitzahl: str = Field(..., max_length=20)
    ort: str = Field(..., max_length=100)
    land: Optional[str] = Field(None, max_length=100, description="Full country name")
    land_iso: str = Field(..., regex="^[A-Z]{2}$", description="ISO 2-letter country code")
    email: Optional[EmailStr] = None
    telefon: Optional[str] = Field(None, max_length=50)

    @validator('land_iso')
    def must_be_eu_country(cls, v):
        """Validate that sender is from EU country."""
        EU_COUNTRIES = [
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
            'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
            'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
        ]
        if v not in EU_COUNTRIES:
            raise ValueError(
                'Sender must be from EU country. Non-EU shipments not supported '
                'in simplified H7 clearance.'
            )
        return v


# ============================================================================
# SECTION 3: RECIPIENT DATA SCHEMAS (Canary Islands)
# ============================================================================

class RecipientDataSchema(BaseModel):
    """Section 3: Empfängerdaten (Kanarische Inseln)"""
    name: str = Field(..., max_length=255)
    strasse_hausnummer: str = Field(..., max_length=255)
    postleitzahl: str = Field(..., max_length=20)
    ort: str = Field(..., max_length=100)
    insel: str = Field(..., max_length=100, description="Canary Island")
    nif_nie_cif: str = Field(..., min_length=5, max_length=50, description="Spanish tax ID")
    email: EmailStr
    telefon: str = Field(..., max_length=50, description="Preferably mobile with country code")


# ============================================================================
# SECTION 4: GOODS DATA SCHEMAS
# ============================================================================

class GoodsPositionSchema(BaseModel):
    """Section 4: Individual goods position"""
    position_nr: int = Field(..., ge=1)
    warenbeschreibung: str = Field(..., min_length=1, max_length=500, description="Detailed, no collective terms")
    warenbeschreibung_es: Optional[str] = Field(None, max_length=500, description="Spanish translation")
    anzahl: int = Field(..., ge=1, description="Quantity >= 1")
    stueckpreis: Decimal = Field(..., ge=0.01, description="Unit price >= 0.01")
    gesamtwert: Decimal = Field(..., ge=0, description="Total value (calculated)")
    ursprungsland_iso: str = Field(..., regex="^[A-Z]{2}$")
    zolltarifnummer: Optional[str] = Field(None, regex="^[0-9]{6,8}$", description="6-8 digit tariff code")
    gewicht: Optional[Decimal] = Field(None, ge=0)
    zustand: Optional[Literal['Neu', 'Gebraucht']] = None

    @validator('gesamtwert', always=True)
    def calculate_total(cls, v, values):
        """Automatically calculate total value."""
        if 'anzahl' in values and 'stueckpreis' in values:
            return Decimal(values['anzahl']) * values['stueckpreis']
        return v


class GoodsDataSchema(BaseModel):
    """Section 4: All goods positions"""
    positions: List[GoodsPositionSchema] = Field(..., min_items=1, description="At least 1 position required")

    @validator('positions')
    def validate_total_value(cls, v):
        """Ensure total value of all positions <= €150."""
        total = sum(p.gesamtwert for p in v)
        if total > 150:
            raise ValueError(
                f'Total value €{total:.2f} exceeds €150 limit for simplified H7 clearance'
            )
        return v


# ============================================================================
# SECTION 5: INVOICE/PROOF SCHEMAS
# ============================================================================

class InvoiceProofB2CSchema(BaseModel):
    """Section 5: Invoice proof for B2C"""
    rechnungsnummer: str = Field(..., max_length=100)
    rechnungsdatum: date
    rechnung_hochgeladen: bool = Field(default=False)
    mwst_ausgewiesen: bool = Field(default=False)
    mwst_warnung_akzeptiert: bool = Field(default=False)
    zahlungsnachweis_file_path: Optional[str] = Field(None, max_length=500)


class InvoiceProofC2CSchema(BaseModel):
    """Section 5: Value proof for C2C"""
    wertangabe_versender: Optional[Decimal] = Field(None, ge=0.01, le=150.00)
    keine_rechnung_vorhanden: bool = Field(..., description="Must be checked")
    schaetzung_geschenk: Optional[Decimal] = Field(None, ge=0.01, le=150.00)

    @validator('keine_rechnung_vorhanden')
    def must_be_true(cls, v):
        """C2C requires confirmation of no invoice."""
        if not v:
            raise ValueError('Declaration "no invoice available" must be confirmed')
        return v

    @validator('schaetzung_geschenk')
    def value_estimate_required(cls, v, values):
        """Either sender value or gift estimate required."""
        if not v and not values.get('wertangabe_versender'):
            raise ValueError('Either sender value declaration or gift estimate required')
        return v


# ============================================================================
# SECTION 6: ADDITIONAL INFO SCHEMAS
# ============================================================================

class AdditionalInfoSchema(BaseModel):
    """Section 6: Additional information"""
    wahrheitserklaerung: bool = Field(..., description="Truth declaration (required)")
    bemerkungen: Optional[str] = Field(None, max_length=5000, description="Comments in Spanish")

    @validator('wahrheitserklaerung')
    def must_be_true(cls, v):
        """Truth declaration must be confirmed."""
        if not v:
            raise ValueError('Truth declaration must be confirmed to proceed')
        return v


# ============================================================================
# FULL FORM SCHEMAS
# ============================================================================

class FullH7FormB2CSchema(BaseModel):
    """Complete H7 form for B2C workflow"""
    workflow: Literal['B2C'] = Field(default='B2C')
    general_data: GeneralDataSchema
    sender_data: SenderDataSchema
    recipient_data: RecipientDataSchema
    goods_data: GoodsDataSchema
    invoice_proof: InvoiceProofB2CSchema
    additional_info: AdditionalInfoSchema


class FullH7FormC2CSchema(BaseModel):
    """Complete H7 form for C2C workflow"""
    workflow: Literal['C2C'] = Field(default='C2C')
    general_data: GeneralDataSchema
    sender_data: SenderDataSchema
    recipient_data: RecipientDataSchema
    goods_data: GoodsDataSchema
    invoice_proof: InvoiceProofC2CSchema
    additional_info: AdditionalInfoSchema


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class H7FormStatusResponse(BaseModel):
    """Response with form status"""
    id: int
    status: str
    workflow: Optional[str]
    validation_errors: Optional[dict]
    created_at: str
    updated_at: str


class ValidationErrorResponse(BaseModel):
    """Validation error details"""
    field: str
    message: str
    code: str  # 'required', 'invalid', 'out_of_range', etc.


class H7FormValidationResponse(BaseModel):
    """Validation response"""
    is_valid: bool
    errors: List[ValidationErrorResponse]
    warnings: List[ValidationErrorResponse]
    block_process: bool  # If true, user cannot proceed
