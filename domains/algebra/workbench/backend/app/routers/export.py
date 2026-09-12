import json
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.domain import ItemAnswerLink, AssessmentItem, AssessmentPart, AnswerEntry, Section, Chapter, SourceSpan, Page
from app.schemas.domain import VerifiedSampleExportSchema

router = APIRouter(prefix="/api", tags=["export"])

@router.get("/export/verified-samples", response_model=List[VerifiedSampleExportSchema])
def export_verified_samples(db: Session = Depends(get_db)):
    links = db.query(ItemAnswerLink).filter(
        ItemAnswerLink.current_status == "verified"
    ).options(
        joinedload(ItemAnswerLink.item).joinedload(AssessmentItem.section).joinedload(Section.chapter),
        joinedload(ItemAnswerLink.item).joinedload(AssessmentItem.source_span).joinedload(SourceSpan.page),
        joinedload(ItemAnswerLink.part).joinedload(AssessmentPart.assessment_item).joinedload(AssessmentItem.section).joinedload(Section.chapter),
        joinedload(ItemAnswerLink.part).joinedload(AssessmentPart.source_span).joinedload(SourceSpan.page),
        joinedload(ItemAnswerLink.answer).joinedload(AnswerEntry.source_span).joinedload(SourceSpan.page)
    ).all()

    exports = []
    for link in links:
        # Determine prompt text, item/part label, section & chapter
        item = link.item
        part = link.part
        answer = link.answer

        if part:
            parent_item = part.assessment_item
            sec = parent_item.section if parent_item else None
            ch = sec.chapter if sec else None

            item_type = parent_item.item_type if parent_item else "question"
            item_label = parent_item.item_label if parent_item else ""
            part_label = part.part_label
            prompt_text = f"{parent_item.content_text} ({part.part_label}) {part.content_text}" if parent_item else part.content_text
            prompt_span = part.source_span or (parent_item.source_span if parent_item else None)
        elif item:
            sec = item.section
            ch = sec.chapter if sec else None

            item_type = item.item_type
            item_label = item.item_label
            part_label = None
            prompt_text = item.content_text
            prompt_span = item.source_span
        else:
            continue

        answer_text = answer.content_text if answer else ""
        answer_span = answer.source_span if answer else None

        # Build provenance object
        provenance = {
            "link_id": link.id,
            "link_method": link.method,
            "link_confidence": link.confidence,
            "prompt_source_span": {
                "id": prompt_span.id if prompt_span else None,
                "page_number": prompt_span.page.page_number if (prompt_span and prompt_span.page) else None,
                "text_content": prompt_span.text_content if prompt_span else None,
                "bbox_json": json.loads(prompt_span.bbox_json) if (prompt_span and prompt_span.bbox_json) else None
            } if prompt_span else None,
            "answer_source_span": {
                "id": answer_span.id if answer_span else None,
                "page_number": answer_span.page.page_number if (answer_span and answer_span.page) else None,
                "text_content": answer_span.text_content if answer_span else None,
                "bbox_json": json.loads(answer_span.bbox_json) if (answer_span and answer_span.bbox_json) else None
            } if answer_span else None
        }

        export_item = VerifiedSampleExportSchema(
            sample_id=f"ekc-sample-{link.id}",
            link_id=link.id,
            item_type=item_type,
            item_label=item_label,
            part_label=part_label,
            chapter_title=ch.title if ch else "",
            section_number=sec.section_number if sec else "",
            section_title=sec.title if sec else "",
            prompt_text=prompt_text,
            answer_text=answer_text,
            verification_status="verified",
            provenance=provenance
        )
        exports.append(export_item)

    return exports
