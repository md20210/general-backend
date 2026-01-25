"""MVP Tax Spain API endpoints for H7 forms and authentication."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import secrets
from uuid import UUID

from backend.database import get_db
from backend.models.user import User
from backend.models.h7form import H7FormData, AdminSettings, PasswordResetToken, EmailVerificationToken
from backend.schemas.h7form import (
    H7FormDataCreate,
    H7FormDataRead,
    AdminSettingsRead,
    AdminSettingsUpdate,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserRegisterExtended,
    UserLogin,
)
from backend.auth.dependencies import current_active_user, require_admin
from backend.services.resend_email_service import resend_email_service
from fastapi_users.password import PasswordHelper


# Create routers
h7_router = APIRouter(prefix="/h7", tags=["h7-forms"])
admin_settings_router = APIRouter(prefix="/admin-settings", tags=["admin-settings"])
mvp_auth_router = APIRouter(prefix="/mvp-auth", tags=["mvp-auth"])

password_helper = PasswordHelper()


# ==================== H7 Form Endpoints ====================

@h7_router.post("/save", response_model=H7FormDataRead)
async def save_h7_form(
    form_data: H7FormDataCreate,
    db: Session = Depends(get_db)
):
    """
    Save H7 form data.

    Can be called by:
    1. Authenticated user (user_id will be set)
    2. Anonymous user with email (user_id will be NULL)

    Email is always required for saving.
    """
    # Create H7 form record (user_id will be NULL for anonymous submissions)
    h7_form = H7FormData(
        user_id=None,  # TODO: Add optional authentication to link user if logged in
        email=form_data.email,
        sendungsart=form_data.sendungsart,
        warenwert_gesamt=form_data.warenwert_gesamt,
        waehrung=form_data.waehrung,
        versandkosten=form_data.versandkosten,
        gesamtbetrag_zoll=form_data.gesamtbetrag_zoll,
        art_lieferung=form_data.art_lieferung,
        absender_name=form_data.absender_name,
        absender_strasse=form_data.absender_strasse,
        absender_plz=form_data.absender_plz,
        absender_ort=form_data.absender_ort,
        absender_land=form_data.absender_land,
        absender_email=form_data.absender_email,
        absender_telefon=form_data.absender_telefon,
        empfaenger_name=form_data.empfaenger_name,
        empfaenger_strasse=form_data.empfaenger_strasse,
        empfaenger_plz=form_data.empfaenger_plz,
        empfaenger_ort=form_data.empfaenger_ort,
        empfaenger_insel=form_data.empfaenger_insel,
        empfaenger_nif=form_data.empfaenger_nif,
        empfaenger_email=form_data.empfaenger_email,
        empfaenger_telefon=form_data.empfaenger_telefon,
        warenpositionen=form_data.warenpositionen,
        exported_pdf_url=form_data.exported_pdf_url,
        wahrheitserklaerung=form_data.wahrheitserklaerung,
    )

    db.add(h7_form)
    db.commit()
    db.refresh(h7_form)

    return h7_form


@h7_router.get("/my-forms", response_model=List[H7FormDataRead])
async def get_my_h7_forms(
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    """Get all H7 forms for authenticated user."""
    stmt = select(H7FormData).where(H7FormData.user_id == user.id).order_by(H7FormData.created_at.desc())
    result = db.execute(stmt)
    forms = result.scalars().all()
    return forms


@h7_router.get("/{form_id}", response_model=H7FormDataRead)
async def get_h7_form(
    form_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    """Get specific H7 form (only if it belongs to user)."""
    stmt = select(H7FormData).where(
        H7FormData.id == form_id,
        H7FormData.user_id == user.id
    )
    result = db.execute(stmt)
    form = result.scalar_one_or_none()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return form


@h7_router.delete("/{form_id}")
async def delete_h7_form(
    form_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    """Delete H7 form (only if it belongs to user)."""
    stmt = select(H7FormData).where(
        H7FormData.id == form_id,
        H7FormData.user_id == user.id
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

    return {"status": "deleted"}


# ==================== Admin Settings Endpoints ====================

@admin_settings_router.get("/", response_model=AdminSettingsRead)
async def get_admin_settings(
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Get admin settings (admin only)."""
    stmt = select(AdminSettings).where(AdminSettings.id == 1)
    result = db.execute(stmt)
    settings = result.scalar_one_or_none()

    if not settings:
        # Create default settings if not exists
        settings = AdminSettings(
            id=1,
            email_sender="michael.dabrock@gmx.es",
            resend_api_key="re_hTZxVL5t_9CcWhbdQLNzCC6aJkd6bd1FW",
            email_verification_required="Ja",
            auto_logout_minutes=30
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@admin_settings_router.put("/", response_model=AdminSettingsRead)
async def update_admin_settings(
    settings_update: AdminSettingsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Update admin settings (admin only)."""
    stmt = select(AdminSettings).where(AdminSettings.id == 1)
    result = db.execute(stmt)
    settings = result.scalar_one_or_none()

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found"
        )

    # Update fields
    if settings_update.email_sender is not None:
        settings.email_sender = settings_update.email_sender
    if settings_update.resend_api_key is not None:
        settings.resend_api_key = settings_update.resend_api_key
    if settings_update.email_verification_required is not None:
        settings.email_verification_required = settings_update.email_verification_required
    if settings_update.auto_logout_minutes is not None:
        settings.auto_logout_minutes = settings_update.auto_logout_minutes

    db.commit()
    db.refresh(settings)

    return settings


# ==================== Custom Password Reset with Resend ====================

@mvp_auth_router.get("/admin/users")
async def list_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Get all users (admin only)."""
    stmt = select(User).order_by(User.email)
    result = db.execute(stmt)
    users = result.scalars().all()

    return {
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "vorname": user.vorname,
                "nachname": user.nachname,
                "sprache": user.sprache,
                "telefonnummer": user.telefonnummer,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "is_superuser": user.is_superuser,
            }
            for user in users
        ],
        "total": len(users)
    }


@mvp_auth_router.post("/admin/users/{user_id}/make-admin")
async def make_user_admin(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Make user an admin (admin only)."""
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    stmt = select(User).where(User.id == user_uuid)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_superuser = True
    db.commit()

    print(f"👑 Admin {admin_user.email} made {user.email} an admin")

    return {
        "status": "success",
        "email": user.email,
        "is_superuser": True
    }


@mvp_auth_router.delete("/admin/users/{user_id}")
async def delete_user_by_admin(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Delete user by ID (admin only)."""
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    stmt = select(User).where(User.id == user_uuid)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found"
        )

    # Prevent deleting yourself
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Delete user (cascades to related records)
    user_email = user.email
    db.delete(user)
    db.commit()

    print(f"🗑️ Admin {admin_user.email} deleted user {user_email}")

    return {
        "status": "deleted",
        "email": user_email,
        "user_id": user_id
    }


@mvp_auth_router.post("/debug/make-admin/{email}")
async def debug_make_user_admin(
    email: str,
    db: Session = Depends(get_db)
):
    """DEBUG: Make user admin by email (NO AUTH CHECK - REMOVE IN PRODUCTION!)"""
    stmt = select(User).where(User.email == email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {email} not found"
        )

    user.is_superuser = True
    user.is_active = True  # Also activate
    user.is_verified = True  # Also verify
    db.commit()

    print(f"👑 DEBUG: Made {email} an admin")

    return {
        "status": "success",
        "email": user.email,
        "is_superuser": True,
        "is_active": True,
        "is_verified": True
    }


@mvp_auth_router.post("/debug/make-admin-query")
async def debug_make_user_admin_query(
    email: str,
    db: Session = Depends(get_db)
):
    """DEBUG: Make user admin by email using query param (NO AUTH CHECK - REMOVE IN PRODUCTION!)"""
    stmt = select(User).where(User.email == email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {email} not found"
        )

    user.is_superuser = True
    user.is_active = True  # Also activate
    user.is_verified = True  # Also verify
    db.commit()

    print(f"👑 DEBUG: Made {email} an admin via query param")

    return {
        "status": "success",
        "email": user.email,
        "is_superuser": True,
        "is_active": True,
        "is_verified": True
    }


@mvp_auth_router.delete("/delete-user/{email}")
async def delete_user_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    """DEBUG: Delete user by email (REMOVE IN PRODUCTION!)"""
    stmt = select(User).where(User.email == email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {email} not found"
        )

    # Delete user (cascades to related records)
    db.delete(user)
    db.commit()

    print(f"🗑️ User {email} deleted")

    return {
        "status": "deleted",
        "email": email,
        "user_id": str(user.id)
    }


@mvp_auth_router.get("/debug-tokens/{email}")
async def debug_tokens(
    email: str,
    db: Session = Depends(get_db)
):
    """DEBUG: Show recent tokens for email (REMOVE IN PRODUCTION!)"""
    stmt = select(User).where(User.email == email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return {"error": "User not found"}

    stmt = select(PasswordResetToken).where(
        PasswordResetToken.user_id == user.id
    ).order_by(PasswordResetToken.created_at.desc()).limit(5)
    result = db.execute(stmt)
    tokens = result.scalars().all()

    return {
        "email": email,
        "user_id": str(user.id),
        "tokens": [
            {
                "id": t.id,
                "token": t.token[:20] + "...",
                "full_token_length": len(t.token),
                "created_at": str(t.created_at),
                "expires_at": str(t.expires_at),
                "used": t.used,
                "is_expired": datetime.now(timezone.utc) > (t.expires_at.replace(tzinfo=timezone.utc) if t.expires_at.tzinfo is None else t.expires_at)
            }
            for t in tokens
        ]
    }


@mvp_auth_router.post("/password-reset-request")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset (public endpoint)."""
    # Find user by email
    stmt = select(User).where(User.email == reset_request.email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Don't reveal if user exists or not (security best practice)
        return {"status": "If email exists, reset link sent"}

    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    print(f"🔑 Creating password reset token for user {user.email}")
    print(f"   Token: {reset_token[:20]}...")
    print(f"   Expires at: {expires_at}")

    # Save token to database
    token_record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
        used="Nein"
    )
    db.add(token_record)
    db.commit()

    print(f"✅ Token saved to database with ID: {token_record.id}")

    # Send email via Resend
    email_sent = await resend_email_service.send_password_reset_email(
        to_email=user.email,
        reset_token=reset_token
    )

    if not email_sent:
        print(f"⚠️ Failed to send password reset email to {user.email}")

    return {"status": "If email exists, reset link sent"}


@mvp_auth_router.post("/password-reset-confirm")
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token."""
    print(f"🔐 Password reset attempt with token: {reset_confirm.token[:20]}...")

    # First check if token exists at all
    stmt_all = select(PasswordResetToken).where(PasswordResetToken.token == reset_confirm.token)
    result_all = db.execute(stmt_all)
    any_token = result_all.scalar_one_or_none()

    if not any_token:
        print(f"❌ Token not found in database")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    print(f"✅ Token found - used: {any_token.used}, expires_at: {any_token.expires_at}")

    # Check if already used
    if any_token.used == "Ja":
        print(f"❌ Token already used")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already used"
        )

    # Check expiration
    now_utc = datetime.now(timezone.utc)
    # Make sure we compare timezone-aware datetimes
    expires_at_aware = any_token.expires_at.replace(tzinfo=timezone.utc) if any_token.expires_at.tzinfo is None else any_token.expires_at
    print(f"⏰ Now: {now_utc}, Expires: {expires_at_aware}")
    if now_utc > expires_at_aware:
        print(f"❌ Token expired")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired"
        )

    token_record = any_token

    # Get user
    stmt = select(User).where(User.id == token_record.user_id)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update password
    user.hashed_password = password_helper.hash(reset_confirm.new_password)

    # Mark token as used
    token_record.used = "Ja"

    db.commit()

    return {"status": "Password reset successful"}


@mvp_auth_router.post("/register-extended")
async def register_user_extended(
    registration: UserRegisterExtended,
    db: Session = Depends(get_db)
):
    """
    Extended registration with profile fields.
    Creates user with vorname, nachname, sprache, telefonnummer.
    """
    # Check if user already exists
    stmt = select(User).where(User.email == registration.email)
    result = db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Create new user (inactive until email verified)
    hashed_password = password_helper.hash(registration.password)

    new_user = User(
        email=registration.email,
        hashed_password=hashed_password,
        vorname=registration.vorname,
        nachname=registration.nachname,
        sprache=registration.sprache,
        telefonnummer=registration.telefonnummer,
        is_active=False,  # User must verify email first
        is_verified=False,
        is_superuser=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate email verification token
    verification_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    print(f"🔑 Creating email verification token for user {new_user.email}")
    print(f"   Token: {verification_token[:20]}...")
    print(f"   Expires at: {expires_at}")

    token_record = EmailVerificationToken(
        user_id=new_user.id,
        token=verification_token,
        expires_at=expires_at,
        used="Nein"
    )
    db.add(token_record)
    db.commit()

    # Send verification email
    email_sent = await resend_email_service.send_registration_email(
        to_email=new_user.email,
        vorname=new_user.vorname,
        nachname=new_user.nachname,
        verification_token=verification_token
    )

    if not email_sent:
        print(f"⚠️ Failed to send verification email to {new_user.email}")

    return {
        "status": "registered",
        "message": "Bitte überprüfen Sie Ihre E-Mail, um Ihr Konto zu aktivieren.",
        "user_id": str(new_user.id),
        "email": new_user.email,
        "email_sent": email_sent
    }


@mvp_auth_router.post("/verify-email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify email address with token."""
    print(f"🔐 Email verification attempt with token: {token[:20]}...")

    # Find token
    stmt = select(EmailVerificationToken).where(EmailVerificationToken.token == token)
    result = db.execute(stmt)
    token_record = result.scalar_one_or_none()

    if not token_record:
        print(f"❌ Token not found in database")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    print(f"✅ Token found - used: {token_record.used}, expires_at: {token_record.expires_at}")

    # Check if already used
    if token_record.used == "Ja":
        print(f"❌ Token already used")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already used"
        )

    # Check expiration
    now_utc = datetime.now(timezone.utc)
    expires_at_aware = token_record.expires_at.replace(tzinfo=timezone.utc) if token_record.expires_at.tzinfo is None else token_record.expires_at
    print(f"⏰ Now: {now_utc}, Expires: {expires_at_aware}")
    if now_utc > expires_at_aware:
        print(f"❌ Token expired")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired"
        )

    # Get user
    stmt = select(User).where(User.id == token_record.user_id)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Activate user
    user.is_active = True
    user.is_verified = True

    # Mark token as used
    token_record.used = "Ja"

    db.commit()

    print(f"✅ User {user.email} verified and activated")

    return {
        "status": "verified",
        "message": "E-Mail erfolgreich bestätigt! Sie können sich jetzt anmelden.",
        "email": user.email
    }


@mvp_auth_router.post("/login")
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    Returns user information and access token on successful login.
    """
    # Find user by email
    stmt = select(User).where(User.email == login_data.email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify password
    is_valid = password_helper.verify_and_update(login_data.password, user.hashed_password)
    if not is_valid[0]:  # verify_and_update returns (is_valid, updated_hash)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    # Check if user is active (email verified)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="E-Mail-Adresse noch nicht bestätigt. Bitte prüfen Sie Ihr Postfach."
        )

    # Generate JWT access token using FastAPI-Users strategy
    from backend.auth.jwt import get_jwt_strategy

    jwt_strategy = get_jwt_strategy()
    token = await jwt_strategy.write_token(user)

    return {
        "status": "logged_in",
        "user_id": str(user.id),
        "email": user.email,
        "vorname": user.vorname,
        "nachname": user.nachname,
        "sprache": user.sprache,
        "is_superuser": user.is_superuser,
        "access_token": token,
        "token_type": "bearer"
    }
