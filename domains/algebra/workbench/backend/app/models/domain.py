import datetime
import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Text, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class ParserEnvironment(Base):
    __tablename__ = "parser_environments"

    id = Column(String, primary_key=True, default=generate_uuid)
    python_version = Column(String, nullable=False)
    git_commit_hash = Column(String, nullable=False)
    package_manifest_hash = Column(String, nullable=False)
    model_checkpoint_id = Column(String, nullable=True)
    created_at = Column(String, default=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    ingestion_runs = relationship("IngestionRun", back_populates="parser_environment")

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    parser_environment_id = Column(String, ForeignKey("parser_environments.id"), nullable=False)
    started_at = Column(String, default=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    completed_at = Column(String, nullable=True)
    status = Column(String, nullable=False, default="running")
    config_json = Column(Text, nullable=True)

    document = relationship("Document", back_populates="ingestion_runs")
    parser_environment = relationship("ParserEnvironment", back_populates="ingestion_runs")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    edition = Column(String, nullable=True)
    file_checksum = Column(String, nullable=True)
    page_count = Column(Integer, nullable=True)
    license = Column(String, nullable=True)

    pages = relationship("Page", back_populates="document", cascade="all, delete-orphan")
    chapters = relationship("Chapter", back_populates="document", cascade="all, delete-orphan")
    ingestion_runs = relationship("IngestionRun", back_populates="document", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "pages"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    image_path = Column(String, nullable=True)
    page_checksum = Column(String, nullable=True)
    pdf_artifact_path = Column(String, nullable=True)
    image_artifact_path = Column(String, nullable=True)
    page_type_classification = Column(String, nullable=True)

    document = relationship("Document", back_populates="pages")
    source_spans = relationship("SourceSpan", back_populates="page", cascade="all, delete-orphan")

class SourceSpan(Base):
    __tablename__ = "source_spans"

    id = Column(String, primary_key=True, default=generate_uuid)
    page_id = Column(String, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    text_content = Column(Text, nullable=False)
    reading_order = Column(Integer, nullable=False, default=0)
    bbox_json = Column(Text, nullable=True)
    extraction_metadata_json = Column(Text, nullable=True)

    page = relationship("Page", back_populates="source_spans")

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    source_span_id = Column(String, ForeignKey("source_spans.id", ondelete="SET NULL"), nullable=True)

    document = relationship("Document", back_populates="chapters")
    source_span = relationship("SourceSpan")
    sections = relationship("Section", back_populates="chapter", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = "sections"

    id = Column(String, primary_key=True, default=generate_uuid)
    chapter_id = Column(String, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    section_number = Column(String, nullable=False)
    title = Column(String, nullable=False)
    source_span_id = Column(String, ForeignKey("source_spans.id", ondelete="SET NULL"), nullable=True)

    chapter = relationship("Chapter", back_populates="sections")
    source_span = relationship("SourceSpan")
    assessment_items = relationship("AssessmentItem", back_populates="section", cascade="all, delete-orphan")

class AssessmentItem(Base):
    __tablename__ = "assessment_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    section_id = Column(String, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    parent_item_id = Column(String, ForeignKey("assessment_items.id", ondelete="CASCADE"), nullable=True)
    ingestion_run_id = Column(String, ForeignKey("ingestion_runs.id", ondelete="CASCADE"), nullable=True)
    item_label = Column(String, nullable=False)
    item_type = Column(String, nullable=False, default="question")  # question, worked_example, try_it
    content_text = Column(Text, nullable=False)
    ordering = Column(Integer, nullable=False, default=0)
    source_span_id = Column(String, ForeignKey("source_spans.id", ondelete="SET NULL"), nullable=True)

    section = relationship("Section", back_populates="assessment_items")
    source_span = relationship("SourceSpan")
    ingestion_run = relationship("IngestionRun")
    parent_item = relationship("AssessmentItem", remote_side=[id], backref="child_items")
    parts = relationship("AssessmentPart", back_populates="assessment_item", cascade="all, delete-orphan")
    links = relationship("ItemAnswerLink", back_populates="item", cascade="all, delete-orphan")

class AssessmentPart(Base):
    __tablename__ = "assessment_parts"

    id = Column(String, primary_key=True, default=generate_uuid)
    item_id = Column(String, ForeignKey("assessment_items.id", ondelete="CASCADE"), nullable=False)
    part_label = Column(String, nullable=False)  # a, b, c
    content_text = Column(Text, nullable=False)
    ordering = Column(Integer, nullable=False, default=0)
    source_span_id = Column(String, ForeignKey("source_spans.id", ondelete="SET NULL"), nullable=True)

    assessment_item = relationship("AssessmentItem", back_populates="parts")
    source_span = relationship("SourceSpan")
    links = relationship("ItemAnswerLink", back_populates="part", cascade="all, delete-orphan")

class AnswerEntry(Base):
    __tablename__ = "answer_entries"

    id = Column(String, primary_key=True, default=generate_uuid)
    ingestion_run_id = Column(String, ForeignKey("ingestion_runs.id", ondelete="CASCADE"), nullable=True)
    answer_label = Column(String, nullable=True)
    content_text = Column(Text, nullable=False)
    source_span_id = Column(String, ForeignKey("source_spans.id", ondelete="SET NULL"), nullable=True)

    source_span = relationship("SourceSpan")
    ingestion_run = relationship("IngestionRun")
    links = relationship("ItemAnswerLink", back_populates="answer")

class ItemAnswerLink(Base):
    __tablename__ = "item_answer_links"

    id = Column(String, primary_key=True, default=generate_uuid)
    ingestion_run_id = Column(String, ForeignKey("ingestion_runs.id", ondelete="CASCADE"), nullable=True)
    item_id = Column(String, ForeignKey("assessment_items.id", ondelete="CASCADE"), nullable=True)
    part_id = Column(String, ForeignKey("assessment_parts.id", ondelete="CASCADE"), nullable=True)
    answer_id = Column(String, ForeignKey("answer_entries.id", ondelete="CASCADE"), nullable=False)
    method = Column(String, nullable=False, default="parser_heuristic")
    confidence = Column(Float, nullable=False, default=1.0)
    current_status = Column(String, nullable=False, default="candidate")  # candidate, reviewed, verified, rejected, needs_resolution

    item = relationship("AssessmentItem", back_populates="links")
    part = relationship("AssessmentPart", back_populates="links")
    answer = relationship("AnswerEntry", back_populates="links")
    ingestion_run = relationship("IngestionRun")
    review_events = relationship("ReviewEvent", back_populates="link", cascade="all, delete-orphan")

class ReviewEvent(Base):
    __tablename__ = "review_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    link_id = Column(String, ForeignKey("item_answer_links.id", ondelete="CASCADE"), nullable=False)
    action = Column(String, nullable=False)  # accept, reject, correct, mark_needs_resolution
    actor = Column(String, nullable=False)
    timestamp = Column(String, default=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    rationale = Column(Text, nullable=True)
    target_answer_id = Column(String, ForeignKey("answer_entries.id", ondelete="SET NULL"), nullable=True)

    link = relationship("ItemAnswerLink", back_populates="review_events")
    target_answer = relationship("AnswerEntry")

class ItemSourceSpan(Base):
    __tablename__ = "item_source_spans"

    item_id = Column(String, ForeignKey("assessment_items.id", ondelete="CASCADE"), primary_key=True)
    source_span_id = Column(String, ForeignKey("source_spans.id", ondelete="CASCADE"), primary_key=True)
    span_order = Column(Integer, nullable=False, default=0)

    item = relationship("AssessmentItem")
    source_span = relationship("SourceSpan")

class AnswerSourceSpan(Base):
    __tablename__ = "answer_source_spans"

    answer_id = Column(String, ForeignKey("answer_entries.id", ondelete="CASCADE"), primary_key=True)
    source_span_id = Column(String, ForeignKey("source_spans.id", ondelete="CASCADE"), primary_key=True)
    span_order = Column(Integer, nullable=False, default=0)

    answer = relationship("AnswerEntry")
    source_span = relationship("SourceSpan")
