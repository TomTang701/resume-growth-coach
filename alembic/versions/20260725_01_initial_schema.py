"""create resume growth coach schema

Revision ID: 20260725_01
Revises:
Create Date: 2026-07-25
"""

from alembic import op
import sqlalchemy as sa


revision = "20260725_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("documents", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("source_type", sa.String(32), nullable=False), sa.Column("filename", sa.String(255)), sa.Column("content", sa.Text(), nullable=False), sa.Column("detected_sections_json", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("job_descriptions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("source_type", sa.String(32), nullable=False), sa.Column("filename", sa.String(255)), sa.Column("content", sa.Text(), nullable=False), sa.Column("detected_keywords_json", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("analyses", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("resume_id", sa.Integer(), sa.ForeignKey("documents.id"), nullable=False), sa.Column("job_description_id", sa.Integer(), sa.ForeignKey("job_descriptions.id"), nullable=False), sa.Column("fit_score", sa.Float(), nullable=False), sa.Column("summary", sa.Text(), nullable=False), sa.Column("model_name", sa.String(128), nullable=False), sa.Column("model_status", sa.String(64), nullable=False), sa.Column("deterministic_result_json", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("skill_matches", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("analysis_id", sa.Integer(), sa.ForeignKey("analyses.id"), nullable=False), sa.Column("match_type", sa.String(32), nullable=False), sa.Column("skill", sa.String(128), nullable=False))
    op.create_table("growth_goals", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("analysis_id", sa.Integer(), sa.ForeignKey("analyses.id"), nullable=False), sa.Column("horizon", sa.String(32), nullable=False), sa.Column("goals_json", sa.Text(), nullable=False))


def downgrade() -> None:
    op.drop_table("growth_goals")
    op.drop_table("skill_matches")
    op.drop_table("analyses")
    op.drop_table("job_descriptions")
    op.drop_table("documents")
