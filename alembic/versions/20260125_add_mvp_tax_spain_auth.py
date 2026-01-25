"""Add MVP Tax Spain authentication and H7 form tables

Revision ID: 20260125_add_mvp_tax_spain_auth
Revises: 20260124_add_tax_case_tables
Create Date: 2026-01-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


# revision identifiers, used by Alembic.
revision = '20260125_add_mvp_tax_spain_auth'
down_revision = '20260124_add_tax_case_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add profile fields to users table
    op.add_column('users', sa.Column('vorname', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('nachname', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('sprache', sa.String(5), nullable=False, server_default='de'))
    op.add_column('users', sa.Column('telefonnummer', sa.String(50), nullable=True))

    # Create h7_form_data table
    op.create_table(
        'h7_form_data',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('email', sa.String(255), nullable=False, index=True),

        # Allgemeine Daten
        sa.Column('sendungsart', sa.String(100), nullable=True),
        sa.Column('warenwert_gesamt', sa.String(50), nullable=True),
        sa.Column('waehrung', sa.String(10), nullable=True),
        sa.Column('versandkosten', sa.String(50), nullable=True),
        sa.Column('gesamtbetrag_zoll', sa.String(50), nullable=True),
        sa.Column('art_lieferung', sa.String(100), nullable=True),

        # Absender
        sa.Column('absender_name', sa.String(255), nullable=True),
        sa.Column('absender_strasse', sa.String(255), nullable=True),
        sa.Column('absender_plz', sa.String(20), nullable=True),
        sa.Column('absender_ort', sa.String(100), nullable=True),
        sa.Column('absender_land', sa.String(100), nullable=True),
        sa.Column('absender_email', sa.String(255), nullable=True),
        sa.Column('absender_telefon', sa.String(50), nullable=True),

        # Empfänger
        sa.Column('empfaenger_name', sa.String(255), nullable=True),
        sa.Column('empfaenger_strasse', sa.String(255), nullable=True),
        sa.Column('empfaenger_plz', sa.String(20), nullable=True),
        sa.Column('empfaenger_ort', sa.String(100), nullable=True),
        sa.Column('empfaenger_insel', sa.String(100), nullable=True),
        sa.Column('empfaenger_nif', sa.String(50), nullable=True),
        sa.Column('empfaenger_email', sa.String(255), nullable=True),
        sa.Column('empfaenger_telefon', sa.String(50), nullable=True),

        # Warenpositionen
        sa.Column('warenpositionen', JSON, nullable=True),

        # Export info
        sa.Column('exported_pdf_url', sa.String(500), nullable=True),
        sa.Column('wahrheitserklaerung', sa.String(10), nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create admin_settings table
    op.create_table(
        'admin_settings',
        sa.Column('id', sa.Integer(), primary_key=True, server_default='1'),
        sa.Column('email_sender', sa.String(255), nullable=False, server_default='michael.dabrock@gmx.es'),
        sa.Column('resend_api_key', sa.String(500), nullable=True),
        sa.Column('email_verification_required', sa.String(10), server_default='Ja'),
        sa.Column('auto_logout_minutes', sa.Integer(), server_default='30'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Insert default admin settings
    op.execute("""
        INSERT INTO admin_settings (id, email_sender, resend_api_key, email_verification_required, auto_logout_minutes)
        VALUES (1, 'michael.dabrock@gmx.es', 're_hTZxVL5t_9CcWhbdQLNzCC6aJkd6bd1FW', 'Ja', 30)
        ON CONFLICT (id) DO NOTHING;
    """)

    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('token', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.String(10), server_default='Nein'),
    )


def downgrade():
    op.drop_table('password_reset_tokens')
    op.drop_table('admin_settings')
    op.drop_table('h7_form_data')

    op.drop_column('users', 'telefonnummer')
    op.drop_column('users', 'sprache')
    op.drop_column('users', 'nachname')
    op.drop_column('users', 'vorname')
