"""Initial schema for Algebra EKC Workbench

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-12 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('edition', sa.String(), nullable=True),
        sa.Column('file_checksum', sa.String(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('license', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'pages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('image_path', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'source_spans',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('page_id', sa.String(), nullable=False),
        sa.Column('text_content', sa.Text(), nullable=False),
        sa.Column('reading_order', sa.Integer(), nullable=False),
        sa.Column('bbox_json', sa.Text(), nullable=True),
        sa.Column('extraction_metadata_json', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'chapters',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('source_span_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_span_id'], ['source_spans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'sections',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('chapter_id', sa.String(), nullable=False),
        sa.Column('section_number', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('source_span_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_span_id'], ['source_spans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'assessment_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('section_id', sa.String(), nullable=False),
        sa.Column('parent_item_id', sa.String(), nullable=True),
        sa.Column('item_label', sa.String(), nullable=False),
        sa.Column('item_type', sa.String(), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('ordering', sa.Integer(), nullable=False),
        sa.Column('source_span_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['parent_item_id'], ['assessment_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_span_id'], ['source_spans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'assessment_parts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('item_id', sa.String(), nullable=False),
        sa.Column('part_label', sa.String(), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('ordering', sa.Integer(), nullable=False),
        sa.Column('source_span_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['assessment_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_span_id'], ['source_spans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'answer_entries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('answer_label', sa.String(), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('source_span_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['source_span_id'], ['source_spans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'item_answer_links',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('item_id', sa.String(), nullable=True),
        sa.Column('part_id', sa.String(), nullable=True),
        sa.Column('answer_id', sa.String(), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('current_status', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['answer_id'], ['answer_entries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['item_id'], ['assessment_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['part_id'], ['assessment_parts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'review_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('link_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('actor', sa.String(), nullable=False),
        sa.Column('timestamp', sa.String(), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('target_answer_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['link_id'], ['item_answer_links.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_answer_id'], ['answer_entries.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('review_events')
    op.drop_table('item_answer_links')
    op.drop_table('answer_entries')
    op.drop_table('assessment_parts')
    op.drop_table('assessment_items')
    op.drop_table('sections')
    op.drop_table('chapters')
    op.drop_table('source_spans')
    op.drop_table('pages')
    op.drop_table('documents')
