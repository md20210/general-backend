"""Add interview_success field to elastic_job_analyses

Revision ID: elasticsearch_003
Revises: elasticsearch_002
Create Date: 2025-12-31 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'elasticsearch_003'
down_revision = 'elasticsearch_002'
branch_labels = None
depends_on = None


def upgrade():
    # Check if column exists first to avoid DuplicateColumnError
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('elastic_job_analyses')]

    # Add interview_success field to elastic_job_analyses table (skip if exists)
    if 'interview_success' not in columns:
        op.add_column('elastic_job_analyses',
                      sa.Column('interview_success', postgresql.JSONB(astext_type=sa.Text()),
                               nullable=True))


def downgrade():
    # Remove interview_success field (with existence check)
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('elastic_job_analyses')]

    if 'interview_success' in columns:
        op.drop_column('elastic_job_analyses', 'interview_success')
