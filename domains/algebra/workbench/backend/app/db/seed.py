import json
import os
from sqlalchemy.orm import Session
from app.config import SEED_FILE
from app.models.domain import (
    Document, Page, SourceSpan, Chapter, Section,
    AssessmentItem, AssessmentPart, AnswerEntry,
    ItemAnswerLink, ReviewEvent
)
from app.db.session import SessionLocal, engine, Base

def seed_db(db: Session = None):
    if db is None:
        db = SessionLocal()
        close_on_exit = True
    else:
        close_on_exit = False

    try:
        # Check if already seeded
        if db.query(Document).first() is not None:
            print("Database already contains data. Skipping seed.")
            return

        if not os.path.exists(SEED_FILE):
            print(f"Seed file {SEED_FILE} not found!")
            return

        with open(SEED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 1. Document
        doc_data = data["document"]
        doc = Document(
            title=doc_data["title"],
            edition=doc_data.get("edition"),
            file_checksum=doc_data.get("file_checksum"),
            page_count=doc_data.get("page_count"),
            license=doc_data.get("license")
        )
        db.add(doc)
        db.flush()

        # 2. Pages
        for page_d in data.get("pages", []):
            p = Page(
                id=page_d["id"],
                document_id=doc.id,
                page_number=page_d["page_number"],
                image_path=page_d.get("image_path")
            )
            db.add(p)
        db.flush()

        # 3. Source Spans
        for span_d in data.get("source_spans", []):
            sp = SourceSpan(
                id=span_d["id"],
                page_id=span_d["page_id"],
                text_content=span_d["text_content"],
                reading_order=span_d.get("reading_order", 0),
                bbox_json=span_d.get("bbox_json"),
                extraction_metadata_json=span_d.get("extraction_metadata_json")
            )
            db.add(sp)
        db.flush()

        # 4. Chapters
        for ch_d in data.get("chapters", []):
            ch = Chapter(
                id=ch_d["id"],
                document_id=doc.id,
                chapter_number=ch_d["chapter_number"],
                title=ch_d["title"],
                source_span_id=ch_d.get("source_span_id")
            )
            db.add(ch)
        db.flush()

        # 5. Sections
        for sec_d in data.get("sections", []):
            sec = Section(
                id=sec_d["id"],
                chapter_id=sec_d["chapter_id"],
                section_number=sec_d["section_number"],
                title=sec_d["title"],
                source_span_id=sec_d.get("source_span_id")
            )
            db.add(sec)
        db.flush()

        # 6. Assessment Items
        for item_d in data.get("assessment_items", []):
            item = AssessmentItem(
                id=item_d["id"],
                section_id=item_d["section_id"],
                parent_item_id=item_d.get("parent_item_id"),
                item_label=item_d["item_label"],
                item_type=item_d.get("item_type", "question"),
                content_text=item_d["content_text"],
                ordering=item_d.get("ordering", 0),
                source_span_id=item_d.get("source_span_id")
            )
            db.add(item)
        db.flush()

        # 7. Assessment Parts
        for part_d in data.get("assessment_parts", []):
            part = AssessmentPart(
                id=part_d["id"],
                item_id=part_d["item_id"],
                part_label=part_d["part_label"],
                content_text=part_d["content_text"],
                ordering=part_d.get("ordering", 0),
                source_span_id=part_d.get("source_span_id")
            )
            db.add(part)
        db.flush()

        # 8. Answer Entries
        for ans_d in data.get("answer_entries", []):
            ans = AnswerEntry(
                id=ans_d["id"],
                answer_label=ans_d.get("answer_label"),
                content_text=ans_d["content_text"],
                source_span_id=ans_d.get("source_span_id")
            )
            db.add(ans)
        db.flush()

        # 9. Item Answer Links
        for link_d in data.get("item_answer_links", []):
            link = ItemAnswerLink(
                id=link_d["id"],
                item_id=link_d.get("item_id"),
                part_id=link_d.get("part_id"),
                answer_id=link_d["answer_id"],
                method=link_d.get("method", "parser_heuristic"),
                confidence=link_d.get("confidence", 1.0),
                current_status=link_d.get("current_status", "candidate")
            )
            db.add(link)
        db.flush()

        # 10. Review Events
        for rev_d in data.get("review_events", []):
            rev = ReviewEvent(
                id=rev_d["id"],
                link_id=rev_d["link_id"],
                action=rev_d["action"],
                actor=rev_d["actor"],
                timestamp=rev_d["timestamp"],
                rationale=rev_d.get("rationale"),
                target_answer_id=rev_d.get("target_answer_id")
            )
            db.add(rev)
        db.flush()

        db.commit()
        print("Database populated successfully with mock seed data.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        if close_on_exit:
            db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_db()
