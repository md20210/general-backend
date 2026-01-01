"""Add Elasticsearch Showcase tables

Revision ID: elasticsearch_001
Revises: 20251229_005333
Create Date: 2025-12-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'elasticsearch_001'
down_revision = 'add_docs_field_001'  # Updated to use shortened revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Check if tables exist first to avoid DuplicateTableError
    bind = op.get_bind()
    inspector = inspect(bind)

    # Create elastic_user_profiles table (skip if exists)
    if 'elastic_user_profiles' not in inspector.get_table_names():
        op.create_table(
            'elastic_user_profiles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('cv_text', sa.Text(), nullable=True),
            sa.Column('cover_letter_text', sa.Text(), nullable=True),
            sa.Column('homepage_url', sa.String(), nullable=True),
            sa.Column('linkedin_url', sa.String(), nullable=True),
            sa.Column('skills_extracted', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
            sa.Column('experience_years', sa.Integer(), nullable=True),
            sa.Column('education_level', sa.String(), nullable=True),
            sa.Column('job_titles', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_elastic_user_profiles_user_id'), 'elastic_user_profiles', ['user_id'], unique=True)

    # Create elastic_job_analyses table (skip if exists)
    if 'elastic_job_analyses' not in inspector.get_table_names():
        op.create_table(
            'elastic_job_analyses',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('job_description', sa.Text(), nullable=False),
            sa.Column('job_url', sa.String(), nullable=True),
            sa.Column('chromadb_results', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
            sa.Column('chromadb_search_time_ms', sa.Float(), nullable=True),
            sa.Column('chromadb_matches_count', sa.Integer(), nullable=True),
            sa.Column('chromadb_relevance_score', sa.Float(), nullable=True),
            sa.Column('elasticsearch_results', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
            sa.Column('elasticsearch_search_time_ms', sa.Float(), nullable=True),
            sa.Column('elasticsearch_matches_count', sa.Integer(), nullable=True),
            sa.Column('elasticsearch_relevance_score', sa.Float(), nullable=True),
            sa.Column('fuzzy_matches', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
            sa.Column('synonym_matches', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
            sa.Column('skill_clusters', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
            sa.Column('performance_comparison', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
            sa.Column('feature_comparison', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('provider', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_elastic_job_analyses_user_id'), 'elastic_job_analyses', ['user_id'], unique=False)


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if 'elastic_job_analyses' in inspector.get_table_names():
        op.drop_index(op.f('ix_elastic_job_analyses_user_id'), table_name='elastic_job_analyses')
        op.drop_table('elastic_job_analyses')

    if 'elastic_user_profiles' in inspector.get_table_names():
        op.drop_index(op.f('ix_elastic_user_profiles_user_id'), table_name='elastic_user_profiles')
        op.drop_table('elastic_user_profiles')
