from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.domain import AssessmentItem, Section, SourceSpan
from app.schemas.domain import AssessmentItemSchema, SourceSpanSchema

router = APIRouter(prefix="/api", tags=["items"])

def enrich_source_span(span: SourceSpan) -> Optional[SourceSpanSchema]:
    if not span:
        return None
    return SourceSpanSchema(
        id=span.id,
        page_id=span.page_id,
        page_number=span.page.page_number if span.page else None,
        text_content=span.text_content,
        reading_order=span.reading_order,
        bbox_json=span.bbox_json,
        extraction_metadata_json=span.extraction_metadata_json
    )

from app.models.domain import AssessmentItem, Section, SourceSpan, AssessmentPart, ItemAnswerLink, AnswerEntry

@router.get("/sections/{section_id}/items", response_model=List[AssessmentItemSchema])
def get_section_items(section_id: str, db: Session = Depends(get_db)):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")

    items = db.query(AssessmentItem).filter(
        AssessmentItem.section_id == section_id
    ).options(
        joinedload(AssessmentItem.source_span).joinedload(SourceSpan.page),
        joinedload(AssessmentItem.parts).joinedload(AssessmentPart.source_span).joinedload(SourceSpan.page),
        joinedload(AssessmentItem.parts).joinedload(AssessmentPart.links).joinedload(ItemAnswerLink.answer).joinedload(AnswerEntry.source_span).joinedload(SourceSpan.page),
        joinedload(AssessmentItem.links).joinedload(ItemAnswerLink.answer).joinedload(AnswerEntry.source_span).joinedload(SourceSpan.page)
    ).order_by(AssessmentItem.ordering).all()

    return items


@router.get("/items/{item_id}", response_model=AssessmentItemSchema)
def get_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(AssessmentItem).filter(
        AssessmentItem.id == item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item
