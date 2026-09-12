from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

class SourceSpanSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_id: str
    page_number: Optional[int] = None
    text_content: str
    reading_order: int
    bbox_json: Optional[str] = None
    extraction_metadata_json: Optional[str] = None

class AnswerEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    answer_label: Optional[str] = None
    content_text: str
    source_span_id: Optional[str] = None
    source_span: Optional[SourceSpanSchema] = None

class ReviewEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    link_id: str
    action: str
    actor: str
    timestamp: str
    rationale: Optional[str] = None
    target_answer_id: Optional[str] = None
    target_answer: Optional[AnswerEntrySchema] = None

class ItemAnswerLinkSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    item_id: Optional[str] = None
    part_id: Optional[str] = None
    answer_id: str
    method: str
    confidence: float
    current_status: str
    answer: Optional[AnswerEntrySchema] = None
    review_events: List[ReviewEventSchema] = []

class AssessmentPartSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    item_id: str
    part_label: str
    content_text: str
    ordering: int
    source_span_id: Optional[str] = None
    source_span: Optional[SourceSpanSchema] = None
    links: List[ItemAnswerLinkSchema] = []

class AssessmentItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    section_id: str
    parent_item_id: Optional[str] = None
    item_label: str
    item_type: str
    content_text: str
    ordering: int
    source_span_id: Optional[str] = None
    source_span: Optional[SourceSpanSchema] = None
    parts: List[AssessmentPartSchema] = []
    links: List[ItemAnswerLinkSchema] = []

class SectionSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chapter_id: str
    section_number: str
    title: str
    candidate_count: int = 0
    reviewed_count: int = 0
    verified_count: int = 0
    rejected_count: int = 0
    needs_resolution_count: int = 0

class ChapterHierarchySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chapter_number: int
    title: str
    sections: List[SectionSummarySchema] = []

class ReviewSubmissionSchema(BaseModel):
    action: str = Field(..., description="accept | reject | correct | mark_needs_resolution")
    actor: str = Field(..., description="Name or ID of reviewer")
    rationale: Optional[str] = Field(None, description="Optional explanation for decision")
    replacement_answer_id: Optional[str] = Field(None, description="Answer entry ID if action is 'correct'")

class VerifiedSampleExportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sample_id: str
    link_id: str
    item_type: str
    item_label: str
    part_label: Optional[str] = None
    chapter_title: str
    section_number: str
    section_title: str
    prompt_text: str
    answer_text: str
    verification_status: str
    provenance: Any
