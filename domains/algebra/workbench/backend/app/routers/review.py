import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.domain import ItemAnswerLink, ReviewEvent, AnswerEntry
from app.schemas.domain import ItemAnswerLinkSchema, ReviewSubmissionSchema

router = APIRouter(prefix="/api", tags=["review"])

@router.get("/review-queue", response_model=List[ItemAnswerLinkSchema])
def get_review_queue(
    status: Optional[str] = Query(None, description="Filter by status (e.g. candidate, needs_resolution, rejected, verified)"),
    db: Session = Depends(get_db)
):
    query = db.query(ItemAnswerLink).options(
        joinedload(ItemAnswerLink.answer).joinedload(AnswerEntry.source_span),
        joinedload(ItemAnswerLink.item),
        joinedload(ItemAnswerLink.part),
        joinedload(ItemAnswerLink.review_events)
    )

    if status:
        query = query.filter(ItemAnswerLink.current_status == status)
    else:
        # Default review queue returns candidate, needs_resolution, and rejected items
        query = query.filter(ItemAnswerLink.current_status.in_(["candidate", "needs_resolution", "rejected"]))

    links = query.order_by(ItemAnswerLink.confidence.asc()).all()
    return links

@router.post("/links/{link_id}/review", response_model=ItemAnswerLinkSchema)
def submit_link_review(
    link_id: str,
    submission: ReviewSubmissionSchema,
    db: Session = Depends(get_db)
):
    link = db.query(ItemAnswerLink).filter(ItemAnswerLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="ItemAnswerLink not found")

    action = submission.action.lower()
    if action not in ["accept", "reject", "correct", "mark_needs_resolution"]:
        raise HTTPException(status_code=400, detail=f"Invalid action '{action}'")

    target_answer_id = submission.replacement_answer_id

    # If action is correct and replacement_answer_id provided, verify answer exists
    if action == "correct" and target_answer_id:
        ans = db.query(AnswerEntry).filter(AnswerEntry.id == target_answer_id).first()
        if not ans:
            raise HTTPException(status_code=404, detail=f"Target AnswerEntry '{target_answer_id}' not found")
        link.answer_id = target_answer_id

    # Update status based on action
    if action == "accept":
        link.current_status = "verified"
    elif action == "reject":
        link.current_status = "rejected"
    elif action == "correct":
        link.current_status = "verified"
    elif action == "mark_needs_resolution":
        link.current_status = "needs_resolution"

    # Append review event
    event = ReviewEvent(
        id=str(uuid.uuid4()),
        link_id=link.id,
        action=action,
        actor=submission.actor,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        rationale=submission.rationale,
        target_answer_id=target_answer_id
    )
    db.add(event)
    db.commit()
    db.refresh(link)

    return link
