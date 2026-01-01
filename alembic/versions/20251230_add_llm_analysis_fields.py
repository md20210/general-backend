"""Add LLM analysis fields to elastic_job_analyses

Revision ID: elasticsearch_002
Revises: elasticsearch_001
Create Date: 2025-12-30 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'elasticsearch_002'
down_revision = 'elasticsearch_001'
branch_labels = None
depends_on = None


def upgrade():
    # Check if columns exist first to avoid DuplicateColumnError
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('elastic_job_analyses')]

    # Add LLM analysis fields to elastic_job_analyses table (skip if exist)
    if 'job_analysis' not in columns:
        op.add_column('elastic_job_analyses',
                      sa.Column('job_analysis', postgresql.JSONB(astext_type=sa.Text()),
                               nullable=False, server_default='{}'))
    if 'fit_score' not in columns:
        op.add_column('elastic_job_analyses',
                      sa.Column('fit_score', postgresql.JSONB(astext_type=sa.Text()),
                               nullable=False, server_default='{}'))
    if 'success_probability' not in columns:
        op.add_column('elastic_job_analyses',
                      sa.Column('success_probability', postgresql.JSONB(astext_type=sa.Text()),
                               nullable=False, server_default='{}'))


def downgrade():
    # Remove LLM analysis fields (with existence checks)
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('elastic_job_analyses')]

    if 'success_probability' in columns:
        op.drop_column('elastic_job_analyses', 'success_probability')
    if 'fit_score' in columns:
        op.drop_column('elastic_job_analyses', 'fit_score')
    if 'job_analysis' in columns:
        op.drop_column('elastic_job_analyses', 'job_analysis')
