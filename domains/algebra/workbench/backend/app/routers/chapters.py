from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Chapter, Section, AssessmentItem, AssessmentPart, ItemAnswerLink
from app.schemas.domain import ChapterHierarchySchema, SectionSummarySchema

router = APIRouter(prefix="/api", tags=["chapters"])

@router.get("/chapters", response_model=List[ChapterHierarchySchema])
def get_chapters(db: Session = Depends(get_db)):
    chapters = db.query(Chapter).order_by(Chapter.chapter_number).all()
    result = []

    for ch in chapters:
        sections_out = []
        sections = db.query(Section).filter(Section.chapter_id == ch.id).order_by(Section.section_number).all()

        for sec in sections:
            # Query all links for items or parts in this section
            items_in_sec = db.query(AssessmentItem).filter(AssessmentItem.section_id == sec.id).all()
            item_ids = [i.id for i in items_in_sec]

            parts_in_sec = db.query(AssessmentPart).filter(AssessmentPart.item_id.in_(item_ids)).all() if item_ids else []
            part_ids = [p.id for p in parts_in_sec]

            links = []
            if item_ids or part_ids:
                links = db.query(ItemAnswerLink).filter(
                    (ItemAnswerLink.item_id.in_(item_ids)) | (ItemAnswerLink.part_id.in_(part_ids))
                ).all()

            counts = {
                "candidate": 0,
                "reviewed": 0,
                "verified": 0,
                "rejected": 0,
                "needs_resolution": 0
            }

            for l in links:
                status = l.current_status
                if status in counts:
                    counts[status] += 1

            sec_schema = SectionSummarySchema(
                id=sec.id,
                chapter_id=sec.chapter_id,
                section_number=sec.section_number,
                title=sec.title,
                candidate_count=counts["candidate"],
                reviewed_count=counts["reviewed"],
                verified_count=counts["verified"],
                rejected_count=counts["rejected"],
                needs_resolution_count=counts["needs_resolution"]
            )
            sections_out.append(sec_schema)

        ch_schema = ChapterHierarchySchema(
            id=ch.id,
            chapter_number=ch.chapter_number,
            title=ch.title,
            sections=sections_out
        )
        result.append(ch_schema)

    return result
