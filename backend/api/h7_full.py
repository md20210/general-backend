"""API endpoints for full H7 form implementation with goods positions."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)

from backend.database import get_db, get_async_session
from backend.models.user import User
from backend.models.h7form import H7FormData, GoodsPosition
from backend.schemas.h7_full_form import (
    FullH7FormB2CSchema,
    FullH7FormC2CSchema,
    H7FormStatusResponse,
    H7FormValidationResponse,
    ValidationErrorResponse,
)
from backend.auth.dependencies import current_active_user

router = APIRouter(prefix="/h7-full", tags=["h7-full-forms"])


# ==================== Debug Endpoint ====================

@router.get("/debug/table-structure")
async def debug_table_structure(db: Session = Depends(get_db)):
    """Debug endpoint to check H7FormData table structure."""
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(db.bind)

        # Get columns for h7_form_data
        columns = inspector.get_columns('h7_form_data')

        # Also check if goods_positions table exists
        tables = inspector.get_table_names()

        # Try a simple query
        result = db.execute(text("SELECT COUNT(*) FROM h7_form_data"))
        count = result.scalar()

        return {
            "h7_form_data_columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"]
                }
                for col in columns
            ],
            "tables": tables,
            "h7_form_data_count": count,
            "goods_positions_exists": "goods_positions" in tables
        }
    except Exception as e:
        logger.error(f"Debug error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug error: {str(e)}"
        )


@router.post("/debug/test-insert")
async def debug_test_insert(db: Session = Depends(get_db)):
    """Debug endpoint to test simple H7FormData insert without goods positions."""
    try:
        # Try raw SQL insert first
        result = db.execute(text("""
            INSERT INTO h7_form_data (email, workflow, warenwert_gesamt, waehrung, versandkosten, art_lieferung,
                absender_name, absender_strasse, absender_plz, absender_ort, absender_land_iso,
                empfaenger_name, empfaenger_strasse, empfaenger_plz, empfaenger_ort, empfaenger_insel, empfaenger_nif, empfaenger_email, empfaenger_telefon,
                wahrheitserklaerung, status)
            VALUES ('test@test.com', 'B2C', 100.50, 'EUR', 10.00, 'Kauf',
                'Test GmbH', 'Test 1', '12345', 'Berlin', 'DE',
                'Test User', 'Test 2', '38001', 'Santa Cruz', 'Tenerife', 'Y1234567Z', 'test@test.com', '+34666777888',
                true, 'draft')
            RETURNING id
        """))
        new_id = result.scalar()
        db.commit()

        return {"success": True, "id": new_id, "message": "Raw SQL insert worked"}
    except Exception as e:
        db.rollback()
        logger.error(f"Debug insert error: {str(e)}")
        return {"success": False, "error": str(e)}


@router.post("/save-b2c-async", response_model=H7FormStatusResponse)
async def save_h7_form_b2c_async(
    form_data: FullH7FormB2CSchema,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Save complete H7 form with B2C workflow using async/asyncpg.
    This avoids psycopg2 type introspection issues.
    """
    try:
        from datetime import datetime, timezone

        # Insert main H7 form using raw SQL to avoid ORM type issues
        result = await db.execute(text("""
            INSERT INTO h7_form_data (
                email, workflow, sendungsart, warenwert_gesamt, waehrung, versandkosten,
                versicherungskosten, gesamtbetrag_zoll, art_lieferung,
                absender_name, absender_strasse, absender_plz, absender_ort, absender_land, absender_land_iso,
                absender_email, absender_telefon,
                empfaenger_name, empfaenger_strasse, empfaenger_plz, empfaenger_ort, empfaenger_insel,
                empfaenger_nif, empfaenger_email, empfaenger_telefon,
                rechnungsnummer, rechnungsdatum, rechnung_hochgeladen, mwst_ausgewiesen, mwst_warnung_akzeptiert,
                zahlungsnachweis_file_path,
                wahrheitserklaerung, bemerkungen, status
            ) VALUES (
                :email, :workflow, :sendungsart, :warenwert_gesamt, :waehrung, :versandkosten,
                :versicherungskosten, :gesamtbetrag_zoll, :art_lieferung,
                :absender_name, :absender_strasse, :absender_plz, :absender_ort, :absender_land, :absender_land_iso,
                :absender_email, :absender_telefon,
                :empfaenger_name, :empfaenger_strasse, :empfaenger_plz, :empfaenger_ort, :empfaenger_insel,
                :empfaenger_nif, :empfaenger_email, :empfaenger_telefon,
                :rechnungsnummer, :rechnungsdatum, :rechnung_hochgeladen, :mwst_ausgewiesen, :mwst_warnung_akzeptiert,
                :zahlungsnachweis_file_path,
                :wahrheitserklaerung, :bemerkungen, :status
            ) RETURNING id
        """), {
            "email": form_data.recipient_data.email,
            "workflow": "B2C",
            "sendungsart": form_data.general_data.sendungsart,
            "warenwert_gesamt": float(form_data.general_data.warenwert_gesamt),
            "waehrung": form_data.general_data.waehrung,
            "versandkosten": float(form_data.general_data.versandkosten),
            "versicherungskosten": float(form_data.general_data.versicherungskosten) if form_data.general_data.versicherungskosten else None,
            "gesamtbetrag_zoll": float(form_data.general_data.gesamtbetrag_zoll) if form_data.general_data.gesamtbetrag_zoll else None,
            "art_lieferung": form_data.general_data.art_lieferung,
            "absender_name": form_data.sender_data.name_firma,
            "absender_strasse": form_data.sender_data.strasse_hausnummer,
            "absender_plz": form_data.sender_data.postleitzahl,
            "absender_ort": form_data.sender_data.ort,
            "absender_land": form_data.sender_data.land,
            "absender_land_iso": form_data.sender_data.land_iso,
            "absender_email": form_data.sender_data.email,
            "absender_telefon": form_data.sender_data.telefon,
            "empfaenger_name": form_data.recipient_data.name,
            "empfaenger_strasse": form_data.recipient_data.strasse_hausnummer,
            "empfaenger_plz": form_data.recipient_data.postleitzahl,
            "empfaenger_ort": form_data.recipient_data.ort,
            "empfaenger_insel": form_data.recipient_data.insel,
            "empfaenger_nif": form_data.recipient_data.nif_nie_cif,
            "empfaenger_email": form_data.recipient_data.email,
            "empfaenger_telefon": form_data.recipient_data.telefon,
            "rechnungsnummer": form_data.invoice_proof.rechnungsnummer,
            "rechnungsdatum": form_data.invoice_proof.rechnungsdatum,
            "rechnung_hochgeladen": form_data.invoice_proof.rechnung_hochgeladen,
            "mwst_ausgewiesen": form_data.invoice_proof.mwst_ausgewiesen,
            "mwst_warnung_akzeptiert": form_data.invoice_proof.mwst_warnung_akzeptiert,
            "zahlungsnachweis_file_path": form_data.invoice_proof.zahlungsnachweis_file_path,
            "wahrheitserklaerung": form_data.additional_info.wahrheitserklaerung,
            "bemerkungen": form_data.additional_info.bemerkungen,
            "status": "draft"
        })

        h7_form_id = result.scalar()

        # Insert goods positions
        for pos_data in form_data.goods_data.positions:
            await db.execute(text("""
                INSERT INTO goods_positions (
                    id, h7_form_id, position_nr, warenbeschreibung, warenbeschreibung_es,
                    anzahl, stueckpreis, gesamtwert, ursprungsland_iso, zolltarifnummer,
                    gewicht, zustand
                ) VALUES (
                    :id, :h7_form_id, :position_nr, :warenbeschreibung, :warenbeschreibung_es,
                    :anzahl, :stueckpreis, :gesamtwert, :ursprungsland_iso, :zolltarifnummer,
                    :gewicht, :zustand
                )
            """), {
                "id": str(uuid4()),
                "h7_form_id": h7_form_id,
                "position_nr": pos_data.position_nr,
                "warenbeschreibung": pos_data.warenbeschreibung,
                "warenbeschreibung_es": pos_data.warenbeschreibung_es,
                "anzahl": pos_data.anzahl,
                "stueckpreis": float(pos_data.stueckpreis),
                "gesamtwert": float(pos_data.gesamtwert),
                "ursprungsland_iso": pos_data.ursprungsland_iso,
                "zolltarifnummer": pos_data.zolltarifnummer,
                "gewicht": float(pos_data.gewicht) if pos_data.gewicht else None,
                "zustand": pos_data.zustand
            })

        await db.commit()

        now = datetime.now(timezone.utc)

        return H7FormStatusResponse(
            id=h7_form_id,
            status="draft",
            workflow="B2C",
            validation_errors=None,
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving B2C H7 form (async): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving form: {str(e)}"
        )


# ==================== Create/Save Endpoints ====================

@router.post("/save-b2c", response_model=H7FormStatusResponse)
async def save_h7_form_b2c(
    form_data: FullH7FormB2CSchema,
    db: Session = Depends(get_db)
):
    """
    Save complete H7 form with B2C workflow.

    Creates H7FormData record and associated GoodsPosition records.
    Can be called by authenticated or anonymous users.
    """
    try:
        # Create main H7 form record
        # TODO: Add authentication support - for now always anonymous
        h7_form = H7FormData(
            user_id=None,  # Anonymous submission
            email=form_data.recipient_data.email,

            # Workflow
            workflow='B2C',

            # Section 1: General Data
            sendungsart=form_data.general_data.sendungsart,
            warenwert_gesamt=form_data.general_data.warenwert_gesamt,
            waehrung=form_data.general_data.waehrung,
            versandkosten=form_data.general_data.versandkosten,
            versicherungskosten=form_data.general_data.versicherungskosten,
            gesamtbetrag_zoll=form_data.general_data.gesamtbetrag_zoll,
            art_lieferung=form_data.general_data.art_lieferung,

            # Section 2: Sender Data
            absender_name=form_data.sender_data.name_firma,
            absender_strasse=form_data.sender_data.strasse_hausnummer,
            absender_plz=form_data.sender_data.postleitzahl,
            absender_ort=form_data.sender_data.ort,
            absender_land=form_data.sender_data.land,
            absender_land_iso=form_data.sender_data.land_iso,
            absender_email=form_data.sender_data.email,
            absender_telefon=form_data.sender_data.telefon,

            # Section 3: Recipient Data
            empfaenger_name=form_data.recipient_data.name,
            empfaenger_strasse=form_data.recipient_data.strasse_hausnummer,
            empfaenger_plz=form_data.recipient_data.postleitzahl,
            empfaenger_ort=form_data.recipient_data.ort,
            empfaenger_insel=form_data.recipient_data.insel,
            empfaenger_nif=form_data.recipient_data.nif_nie_cif,
            empfaenger_email=form_data.recipient_data.email,
            empfaenger_telefon=form_data.recipient_data.telefon,

            # Section 5: Invoice Proof (B2C)
            rechnungsnummer=form_data.invoice_proof.rechnungsnummer,
            rechnungsdatum=form_data.invoice_proof.rechnungsdatum,
            rechnung_hochgeladen=form_data.invoice_proof.rechnung_hochgeladen,
            mwst_ausgewiesen=form_data.invoice_proof.mwst_ausgewiesen,
            mwst_warnung_akzeptiert=form_data.invoice_proof.mwst_warnung_akzeptiert,
            zahlungsnachweis_file_path=form_data.invoice_proof.zahlungsnachweis_file_path,

            # Section 6: Additional Info
            wahrheitserklaerung=form_data.additional_info.wahrheitserklaerung,
            bemerkungen=form_data.additional_info.bemerkungen,

            # Status
            status='draft'
        )

        db.add(h7_form)
        db.flush()  # Get h7_form.id without committing

        # Create GoodsPosition records
        for pos_data in form_data.goods_data.positions:
            goods_pos = GoodsPosition(
                h7_form_id=h7_form.id,
                position_nr=pos_data.position_nr,
                warenbeschreibung=pos_data.warenbeschreibung,
                warenbeschreibung_es=pos_data.warenbeschreibung_es,
                anzahl=pos_data.anzahl,
                stueckpreis=pos_data.stueckpreis,
                gesamtwert=pos_data.gesamtwert,
                ursprungsland_iso=pos_data.ursprungsland_iso,
                zolltarifnummer=pos_data.zolltarifnummer,
                gewicht=pos_data.gewicht,
                zustand=pos_data.zustand
            )
            db.add(goods_pos)

        db.commit()
        # Don't refresh - avoid psycopg2 type introspection issues
        # db.refresh(h7_form)

        # Get timestamps from flush
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

        return H7FormStatusResponse(
            id=h7_form.id,
            status='draft',
            workflow='B2C',
            validation_errors=None,
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error saving B2C H7 form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving form: {str(e)}"
        )


@router.post("/save-c2c", response_model=H7FormStatusResponse)
async def save_h7_form_c2c(
    form_data: FullH7FormC2CSchema,
    db: Session = Depends(get_db)
):
    """
    Save complete H7 form with C2C workflow.

    Creates H7FormData record and associated GoodsPosition records.
    Can be called by authenticated or anonymous users.
    """
    try:
        # Create main H7 form record
        # TODO: Add authentication support - for now always anonymous
        h7_form = H7FormData(
            user_id=None,  # Anonymous submission
            email=form_data.recipient_data.email,

            # Workflow
            workflow='C2C',

            # Section 1: General Data
            sendungsart=form_data.general_data.sendungsart,
            warenwert_gesamt=form_data.general_data.warenwert_gesamt,
            waehrung=form_data.general_data.waehrung,
            versandkosten=form_data.general_data.versandkosten,
            versicherungskosten=form_data.general_data.versicherungskosten,
            gesamtbetrag_zoll=form_data.general_data.gesamtbetrag_zoll,
            art_lieferung=form_data.general_data.art_lieferung,

            # Section 2: Sender Data
            absender_name=form_data.sender_data.name_firma,
            absender_strasse=form_data.sender_data.strasse_hausnummer,
            absender_plz=form_data.sender_data.postleitzahl,
            absender_ort=form_data.sender_data.ort,
            absender_land=form_data.sender_data.land,
            absender_land_iso=form_data.sender_data.land_iso,
            absender_email=form_data.sender_data.email,
            absender_telefon=form_data.sender_data.telefon,

            # Section 3: Recipient Data
            empfaenger_name=form_data.recipient_data.name,
            empfaenger_strasse=form_data.recipient_data.strasse_hausnummer,
            empfaenger_plz=form_data.recipient_data.postleitzahl,
            empfaenger_ort=form_data.recipient_data.ort,
            empfaenger_insel=form_data.recipient_data.insel,
            empfaenger_nif=form_data.recipient_data.nif_nie_cif,
            empfaenger_email=form_data.recipient_data.email,
            empfaenger_telefon=form_data.recipient_data.telefon,

            # Section 5: Invoice Proof (C2C)
            wertangabe_versender=form_data.invoice_proof.wertangabe_versender,
            keine_rechnung_vorhanden=form_data.invoice_proof.keine_rechnung_vorhanden,
            schaetzung_geschenk=form_data.invoice_proof.schaetzung_geschenk,

            # Section 6: Additional Info
            wahrheitserklaerung=form_data.additional_info.wahrheitserklaerung,
            bemerkungen=form_data.additional_info.bemerkungen,

            # Status
            status='draft'
        )

        db.add(h7_form)
        db.flush()  # Get h7_form.id without committing

        # Create GoodsPosition records
        for pos_data in form_data.goods_data.positions:
            goods_pos = GoodsPosition(
                h7_form_id=h7_form.id,
                position_nr=pos_data.position_nr,
                warenbeschreibung=pos_data.warenbeschreibung,
                warenbeschreibung_es=pos_data.warenbeschreibung_es,
                anzahl=pos_data.anzahl,
                stueckpreis=pos_data.stueckpreis,
                gesamtwert=pos_data.gesamtwert,
                ursprungsland_iso=pos_data.ursprungsland_iso,
                zolltarifnummer=pos_data.zolltarifnummer,
                gewicht=pos_data.gewicht,
                zustand=pos_data.zustand
            )
            db.add(goods_pos)

        db.commit()
        # Don't refresh - avoid psycopg2 type introspection issues
        # db.refresh(h7_form)

        # Get timestamps from flush
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

        return H7FormStatusResponse(
            id=h7_form.id,
            status='draft',
            workflow='C2C',
            validation_errors=None,
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error saving C2C H7 form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving form: {str(e)}"
        )


# ==================== Retrieve Endpoints ====================

@router.get("/list", response_model=List[H7FormStatusResponse])
async def list_h7_forms(
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    """
    Get all H7 forms for authenticated user.
    Returns list with basic info (no full form data).
    """
    stmt = select(H7FormData).where(
        H7FormData.user_id == current_user.id
    ).order_by(H7FormData.created_at.desc())

    result = db.execute(stmt)
    forms = result.scalars().all()

    return [
        H7FormStatusResponse(
            id=form.id,
            status=form.status,
            workflow=form.workflow,
            validation_errors=form.validation_errors,
            created_at=form.created_at.isoformat(),
            updated_at=form.updated_at.isoformat()
        )
        for form in forms
    ]


@router.get("/{form_id}/status", response_model=H7FormStatusResponse)
async def get_h7_form_status(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    """Get status of specific H7 form."""
    stmt = select(H7FormData).where(
        H7FormData.id == form_id,
        H7FormData.user_id == current_user.id
    )

    result = db.execute(stmt)
    form = result.scalar_one_or_none()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return H7FormStatusResponse(
        id=form.id,
        status=form.status,
        workflow=form.workflow,
        validation_errors=form.validation_errors,
        created_at=form.created_at.isoformat(),
        updated_at=form.updated_at.isoformat()
    )


# ==================== Update/Delete Endpoints ====================

@router.delete("/{form_id}")
async def delete_h7_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    """Delete H7 form and all associated goods positions (cascade)."""
    stmt = select(H7FormData).where(
        H7FormData.id == form_id,
        H7FormData.user_id == current_user.id
    )

    result = db.execute(stmt)
    form = result.scalar_one_or_none()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    db.delete(form)
    db.commit()

    return {"status": "success", "message": f"Form {form_id} deleted"}


@router.post("/{form_id}/submit", response_model=H7FormStatusResponse)
async def submit_h7_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    """
    Submit H7 form for processing.
    Changes status from 'draft' to 'submitted'.
    """
    stmt = select(H7FormData).where(
        H7FormData.id == form_id,
        H7FormData.user_id == current_user.id
    )

    result = db.execute(stmt)
    form = result.scalar_one_or_none()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    if form.status != 'draft':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Form is already {form.status}, cannot submit"
        )

    # TODO: Add validation before submission
    if not form.wahrheitserklaerung:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Truth declaration must be accepted"
        )

    form.status = 'submitted'
    db.commit()
    # Don't refresh - avoid psycopg2 type introspection issues
    # db.refresh(form)

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    return H7FormStatusResponse(
        id=form.id,
        status='submitted',
        workflow=form.workflow,
        validation_errors=form.validation_errors,
        created_at=now.isoformat(),
        updated_at=now.isoformat()
    )


# ==================== Validation Endpoint ====================

@router.post("/{form_id}/validate", response_model=H7FormValidationResponse)
async def validate_h7_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    """
    Validate H7 form against business rules.
    Returns validation errors and warnings.
    """
    stmt = select(H7FormData).where(
        H7FormData.id == form_id,
        H7FormData.user_id == current_user.id
    )

    result = db.execute(stmt)
    form = result.scalar_one_or_none()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    errors: List[ValidationErrorResponse] = []
    warnings: List[ValidationErrorResponse] = []

    # Critical validations
    if not form.wahrheitserklaerung:
        errors.append(ValidationErrorResponse(
            field="wahrheitserklaerung",
            message="Truth declaration must be accepted",
            code="required"
        ))

    if form.warenwert_gesamt > 150:
        errors.append(ValidationErrorResponse(
            field="warenwert_gesamt",
            message="Total value exceeds €150 limit for simplified H7 clearance",
            code="out_of_range"
        ))

    # Check EU country
    EU_COUNTRIES = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                    'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
                    'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']

    if form.absender_land_iso and form.absender_land_iso not in EU_COUNTRIES:
        errors.append(ValidationErrorResponse(
            field="absender_land_iso",
            message="Sender must be from EU country",
            code="invalid"
        ))

    # Warnings
    if form.workflow == 'B2C' and not form.mwst_ausgewiesen:
        warnings.append(ValidationErrorResponse(
            field="mwst_ausgewiesen",
            message="VAT not shown on invoice may cause delays",
            code="warning"
        ))

    block_process = len(errors) > 0

    return H7FormValidationResponse(
        is_valid=not block_process,
        errors=errors,
        warnings=warnings,
        block_process=block_process
    )
