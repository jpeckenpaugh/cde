"""Ingestion pipeline schema for Stage 1 & Stage 2

Revision ID: 002_ingestion_pipeline_schema
Revises: 001_initial_schema
Create Date: 2026-09-12 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_ingestion_pipeline_schema'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Create parser_environments
    op.create_table(
        'parser_environments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('python_version', sa.String(), nullable=False),
        sa.Column('git_commit_hash', sa.String(), nullable=False),
        sa.Column('package_manifest_hash', sa.String(), nullable=False),
        sa.Column('model_checkpoint_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Create ingestion_runs
    op.create_table(
        'ingestion_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('parser_environment_id', sa.String(), nullable=False),
        sa.Column('started_at', sa.String(), nullable=False),
        sa.Column('completed_at', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='running'),
        sa.Column('config_json', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parser_environment_id'], ['parser_environments.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Add expanded columns to pages
    with op.batch_alter_table('pages') as batch_op:
        batch_op.add_column(sa.Column('page_checksum', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('pdf_artifact_path', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('image_artifact_path', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('page_type_classification', sa.String(), nullable=True))

    # 4. Add ingestion_run_id to candidate tables with named foreign keys
    with op.batch_alter_table('assessment_items') as batch_op:
        batch_op.add_column(sa.Column('ingestion_run_id', sa.String(), sa.ForeignKey('ingestion_runs.id', ondelete='CASCADE', name='fk_assessment_items_ingestion_run'), nullable=True))

    with op.batch_alter_table('answer_entries') as batch_op:
        batch_op.add_column(sa.Column('ingestion_run_id', sa.String(), sa.ForeignKey('ingestion_runs.id', ondelete='CASCADE', name='fk_answer_entries_ingestion_run'), nullable=True))

    with op.batch_alter_table('item_answer_links') as batch_op:
        batch_op.add_column(sa.Column('ingestion_run_id', sa.String(), sa.ForeignKey('ingestion_runs.id', ondelete='CASCADE', name='fk_item_answer_links_ingestion_run'), nullable=True))

    # 5. Junction table for item_source_spans
    op.create_table(
        'item_source_spans',
        sa.Column('item_id', sa.String(), nullable=False),
        sa.Column('source_span_id', sa.String(), nullable=False),
        sa.Column('span_order', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['item_id'], ['assessment_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_span_id'], ['source_spans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('item_id', 'source_span_id')
    )

    # 6. Junction table for answer_source_spans
    op.create_table(
        'answer_source_spans',
        sa.Column('answer_id', sa.String(), nullable=False),
        sa.Column('source_span_id', sa.String(), nullable=False),
        sa.Column('span_order', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['answer_id'], ['answer_entries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_span_id'], ['source_spans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('answer_id', 'source_span_id')
    )

def downgrade() -> None:
    op.drop_table('answer_source_spans')
    op.drop_table('item_source_spans')

    with op.batch_alter_table('item_answer_links') as batch_op:
        batch_op.drop_column('ingestion_run_id')

    with op.batch_alter_table('answer_entries') as batch_op:
        batch_op.drop_column('ingestion_run_id')

    with op.batch_alter_table('assessment_items') as batch_op:
        batch_op.drop_column('ingestion_run_id')

    with op.batch_alter_table('pages') as batch_op:
        batch_op.drop_column('page_type_classification')
        batch_op.drop_column('image_artifact_path')
        batch_op.drop_column('pdf_artifact_path')
        batch_op.drop_column('page_checksum')

    op.drop_table('ingestion_runs')
    op.drop_table('parser_environments')
