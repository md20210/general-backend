"""Add LLM analysis fields to elastic_job_analyses

Revision ID: elasticsearch_002
Revises: elasticsearch_001
Create Date: 2025-12-30 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'elasticsearch_002'
down_revision = 'elasticsearch_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add LLM analysis fields to elastic_job_analyses table
    op.add_column('elastic_job_analyses',
                  sa.Column('job_analysis', postgresql.JSONB(astext_type=sa.Text()),
                           nullable=False, server_default='{}'))
    op.add_column('elastic_job_analyses',
                  sa.Column('fit_score', postgresql.JSONB(astext_type=sa.Text()),
                           nullable=False, server_default='{}'))
    op.add_column('elastic_job_analyses',
                  sa.Column('success_probability', postgresql.JSONB(astext_type=sa.Text()),
                           nullable=False, server_default='{}'))


def downgrade():
    # Remove LLM analysis fields
    op.drop_column('elastic_job_analyses', 'success_probability')
    op.drop_column('elastic_job_analyses', 'fit_score')
    op.drop_column('elastic_job_analyses', 'job_analysis')
