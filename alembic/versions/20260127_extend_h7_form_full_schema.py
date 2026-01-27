"""Extend H7 form schema with full fields and goods_positions table

Revision ID: 20260127_extend_h7_form_full_schema
Revises: 20260125_make_michael_admin
Create Date: 2026-01-27 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '20260127_extend_h7_form_full_schema'
down_revision = '20260125_make_michael_admin'
branch_labels = None
depends_on = None


def upgrade():
    """Extend H7FormData table and create GoodsPosition table."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Get existing columns in h7_form_data table
    existing_columns = [col['name'] for col in inspector.get_columns('h7_form_data')]
    
    # Add new columns to h7_form_data if they don't exist
    new_columns = {
        'workflow': (sa.String(10), {'nullable': True}),
        'versicherungskosten': (sa.Numeric(10, 2), {'nullable': True}),
        'absender_land_iso': (sa.String(2), {'nullable': True}),
        'rechnungsnummer': (sa.String(100), {'nullable': True}),
        'rechnungsdatum': (sa.Date(), {'nullable': True}),
        'rechnung_hochgeladen': (sa.Boolean(), {'server_default': 'false'}),
        'mwst_ausgewiesen': (sa.Boolean(), {'server_default': 'false'}),
        'mwst_warnung_akzeptiert': (sa.Boolean(), {'server_default': 'false'}),
        'wertangabe_versender': (sa.Numeric(10, 2), {'nullable': True}),
        'keine_rechnung_vorhanden': (sa.Boolean(), {'server_default': 'false'}),
        'schaetzung_geschenk': (sa.Numeric(10, 2), {'nullable': True}),
        'zahlungsnachweis_file_path': (sa.String(500), {'nullable': True}),
        'bemerkungen': (sa.Text(), {'nullable': True}),
        'status': (sa.String(50), {'server_default': 'draft'}),
        'validation_errors': (sa.JSON(), {'nullable': True}),
    }
    
    for col_name, (col_type, col_kwargs) in new_columns.items():
        if col_name not in existing_columns:
            op.add_column('h7_form_data', sa.Column(col_name, col_type, **col_kwargs))
    
    # Alter existing columns to use Numeric instead of String for monetary values
    # Note: This requires data migration, so we'll keep old data as-is for now
    # In production, you'd want to migrate the data first
    
    # Alter wahrheitserklaerung to Boolean if it's still String
    try:
        # Try to check the column type
        conn.execute(sa.text("""
            ALTER TABLE h7_form_data 
            ALTER COLUMN wahrheitserklaerung TYPE BOOLEAN 
            USING CASE 
                WHEN wahrheitserklaerung = 'Ja' THEN true 
                ELSE false 
            END
        """))
    except:
        # If column doesn't exist or already Boolean, skip
        pass
    
    # Create goods_positions table if it doesn't exist
    existing_tables = inspector.get_table_names()
    
    if 'goods_positions' not in existing_tables:
        op.create_table(
            'goods_positions',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, index=True),
            sa.Column('h7_form_id', sa.Integer(), sa.ForeignKey('h7_form_data.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('position_nr', sa.Integer(), nullable=False),
            sa.Column('warenbeschreibung', sa.String(500), nullable=False),
            sa.Column('warenbeschreibung_es', sa.String(500), nullable=True),
            sa.Column('anzahl', sa.Integer(), nullable=False),
            sa.Column('stueckpreis', sa.Numeric(10, 2), nullable=False),
            sa.Column('gesamtwert', sa.Numeric(10, 2), nullable=False),
            sa.Column('ursprungsland_iso', sa.String(2), nullable=False),
            sa.Column('zolltarifnummer', sa.String(10), nullable=True),
            sa.Column('gewicht', sa.Numeric(10, 2), nullable=True),
            sa.Column('zustand', sa.String(20), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )
        
        # Add unique constraint for position_nr per h7_form
        op.create_unique_constraint(
            'uq_goods_positions_h7_form_position',
            'goods_positions',
            ['h7_form_id', 'position_nr']
        )
        
        # Add check constraints
        op.create_check_constraint(
            'ck_goods_positions_anzahl_positive',
            'goods_positions',
            'anzahl >= 1'
        )
        
        op.create_check_constraint(
            'ck_goods_positions_stueckpreis_positive',
            'goods_positions',
            'stueckpreis >= 0.01'
        )


def downgrade():
    """Remove goods_positions table and new columns from h7_form_data."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Drop goods_positions table
    if 'goods_positions' in existing_tables:
        op.drop_table('goods_positions')
    
    # Drop new columns from h7_form_data
    new_columns = [
        'workflow', 'versicherungskosten', 'absender_land_iso',
        'rechnungsnummer', 'rechnungsdatum', 'rechnung_hochgeladen',
        'mwst_ausgewiesen', 'mwst_warnung_akzeptiert', 'wertangabe_versender',
        'keine_rechnung_vorhanden', 'schaetzung_geschenk',
        'zahlungsnachweis_file_path', 'bemerkungen', 'status', 'validation_errors'
    ]
    
    existing_columns = [col['name'] for col in inspector.get_columns('h7_form_data')]
    
    for col_name in new_columns:
        if col_name in existing_columns:
            op.drop_column('h7_form_data', col_name)
