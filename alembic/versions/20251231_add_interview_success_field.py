"""Add interview_success field to elastic_job_analyses

Revision ID: elasticsearch_003
Revises: elasticsearch_002
Create Date: 2025-12-31 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'elasticsearch_003'
down_revision = 'elasticsearch_002'
branch_labels = None
depends_on = None


def upgrade():
    # Add interview_success field to elastic_job_analyses table
    op.add_column('elastic_job_analyses',
                  sa.Column('interview_success', postgresql.JSONB(astext_type=sa.Text()),
                           nullable=True))


def downgrade():
    # Remove interview_success field
    op.drop_column('elastic_job_analyses', 'interview_success')
