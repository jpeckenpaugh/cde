import os
import sys
import json
import shutil
import hashlib
import argparse
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
import pymupdf as fitz
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.config import ARTIFACTS_DIR, DATA_DIR, SOURCES_DIR
from app.models.domain import (
    Document, Page, SourceSpan, Chapter, Section,
    AssessmentItem, AssessmentPart, AnswerEntry,
    ItemAnswerLink, ReviewEvent, ItemSourceSpan, AnswerSourceSpan,
    ParserEnvironment, IngestionRun, generate_uuid
)

def compute_file_checksum(filepath: Path | str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_git_commit_hash() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True
        )
        return res.stdout.strip()
    except Exception:
        return "unknown"

def compute_package_manifest_hash() -> str:
    req_file = Path(__file__).resolve().parent.parent.parent / "requirements.txt"
    if req_file.exists():
        return compute_file_checksum(req_file)
    return "unknown"

def capture_environment_audit(db: Session) -> ParserEnvironment:
    py_ver = sys.version.split()[0]
    git_hash = get_git_commit_hash()
    manifest_hash = compute_package_manifest_hash()

    env = ParserEnvironment(
        id=generate_uuid(),
        python_version=py_ver,
        git_commit_hash=git_hash,
        package_manifest_hash=manifest_hash,
        model_checkpoint_id=None
    )
    db.add(env)
    db.commit()
    db.refresh(env)
    return env

def reset_database(db: Session, purge_artifacts: bool = False):
    """
    Flushes all relational database tables in reverse dependency order.
    Optionally purges generated artifact files from data/artifacts/.
    """
    db.query(ReviewEvent).delete()
    db.query(ItemAnswerLink).delete()
    db.query(AnswerSourceSpan).delete()
    db.query(ItemSourceSpan).delete()
    db.query(AssessmentPart).delete()
    db.query(AssessmentItem).delete()
    db.query(AnswerEntry).delete()
    db.query(Section).delete()
    db.query(Chapter).delete()
    db.query(SourceSpan).delete()
    db.query(Page).delete()
    db.query(IngestionRun).delete()
    db.query(Document).delete()
    db.query(ParserEnvironment).delete()
    db.commit()

    if purge_artifacts and ARTIFACTS_DIR.exists():
        for item in ARTIFACTS_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

class IngestionProgressTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self._state = {
            "run_id": None,
            "status": "idle",
            "started_at": None,
            "completed_at": None,
            "pages_processed": 0,
            "total_pages": 0,
            "current_page_number": 0,
            "current_section_title": None,
            "error_message": None
        }

    def start_job(self, run_id: str, total_pages: int):
        with self._lock:
            self._state = {
                "run_id": run_id,
                "status": "running",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": None,
                "pages_processed": 0,
                "total_pages": total_pages,
                "current_page_number": 0,
                "current_section_title": None,
                "error_message": None
            }

    def update_progress(self, pages_processed: int, current_page_number: int, current_section_title: str | None = None):
        with self._lock:
            self._state["pages_processed"] = pages_processed
            self._state["current_page_number"] = current_page_number
            if current_section_title:
                self._state["current_section_title"] = current_section_title

    def complete_job(self):
        with self._lock:
            self._state["status"] = "completed"
            self._state["completed_at"] = datetime.now(timezone.utc).isoformat()

    def fail_job(self, error_message: str):
        with self._lock:
            self._state["status"] = "failed"
            self._state["completed_at"] = datetime.now(timezone.utc).isoformat()
            self._state["error_message"] = error_message

    def get_status(self) -> dict:
        with self._lock:
            return dict(self._state)

    def is_running(self) -> bool:
        with self._lock:
            return self._state["status"] == "running"

ingestion_progress_tracker = IngestionProgressTracker()

def parse_page_range(pages_str: str | None, total_pages: int) -> list[int]:
    if not pages_str:
        return list(range(1, total_pages + 1))
    
    pages = set()
    parts = pages_str.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str) if start_str else 1
            end = int(end_str) if end_str else total_pages
            for p in range(start, end + 1):
                if 1 <= p <= total_pages:
                    pages.add(p)
        else:
            if part.isdigit():
                p = int(part)
                if 1 <= p <= total_pages:
                    pages.add(p)
    return sorted(list(pages))

def classify_page_content(text: str) -> str:
    text_lower = text.lower()
    if len(text.strip()) < 20:
        return "scanned"
    if any(k in text_lower for k in ["table of contents", "contents"]):
        return "toc"
    if any(k in text_lower for k in ["answer key", "answers", "odds", "evens"]):
        return "answer_key"
    if any(k in text_lower for k in ["exercise", "exercises", "practice", "chapter review", "try it"]):
        return "exercise_list"
    return "narrative"

def run_stage1_ingestion(
    pdf_path: str | Path,
    pages_arg: str | None = None,
    output_dir: str | Path | None = None,
    db: Session | None = None,
    reset_db: bool = False,
    purge_artifacts: bool = False
) -> dict:
    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")

    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True

    try:
        if reset_db:
            reset_database(db, purge_artifacts=purge_artifacts)

        # 1. SHA-256 Checksum Calculation
        doc_checksum = compute_file_checksum(pdf_path)
        
        # Determine artifact root directory
        base_dir = Path(output_dir).resolve() if output_dir else ARTIFACTS_DIR
        doc_artifact_dir = base_dir / doc_checksum
        doc_artifact_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy source PDF to artifact directory
        dest_source_pdf = doc_artifact_dir / "source.pdf"
        if not dest_source_pdf.exists():
            shutil.copy2(pdf_path, dest_source_pdf)

        # Open PDF with PyMuPDF
        pdf_doc = fitz.open(pdf_path)
        total_pages = len(pdf_doc)

        # 2. Environment Audit & Ingestion Run Record
        env = capture_environment_audit(db)
        
        # 3. Document Registration / Lookup
        document = db.query(Document).filter(Document.file_checksum == doc_checksum).first()
        if not document:
            title = pdf_doc.metadata.get("title") or pdf_path.stem
            document = Document(
                id=generate_uuid(),
                title=title,
                edition="2e",
                file_checksum=doc_checksum,
                page_count=total_pages,
                license="CC BY 4.0"
            )
            db.add(document)
            db.commit()
            db.refresh(document)

        ingestion_run = IngestionRun(
            id=generate_uuid(),
            document_id=document.id,
            parser_environment_id=env.id,
            status="running",
            config_json=json.dumps({"pages_arg": pages_arg, "source_file": str(pdf_path)})
        )
        db.add(ingestion_run)
        db.commit()

        # Parse target page numbers
        target_pages = parse_page_range(pages_arg, total_pages)
        pages_artifact_dir = doc_artifact_dir / "pages"
        pages_artifact_dir.mkdir(parents=True, exist_ok=True)

        ingestion_progress_tracker.start_job(
            run_id=ingestion_run.id,
            total_pages=len(target_pages)
        )

        pages_summary = []

        for processed_idx, p_num in enumerate(target_pages, 1):
            ingestion_progress_tracker.update_progress(
                pages_processed=processed_idx,
                current_page_number=p_num
            )
            p_idx = p_num - 1
            page = pdf_doc[p_idx]
            page_dir = pages_artifact_dir / f"page_{p_num:04d}"
            page_dir.mkdir(parents=True, exist_ok=True)

            # Single page PDF extraction
            page_pdf_path = page_dir / "page.pdf"
            single_doc = fitz.open()
            single_doc.insert_pdf(pdf_doc, from_page=p_idx, to_page=p_idx)
            single_doc.save(page_pdf_path)
            single_doc.close()

            page_checksum = compute_file_checksum(page_pdf_path)

            # Render 300 DPI PNG
            page_png_path = page_dir / "page.png"
            pix = page.get_pixmap(dpi=300)
            pix.save(page_png_path)

            # Extract layout text blocks & bounding boxes
            rect = page.rect
            width, height = rect.width, rect.height
            text_blocks = page.get_text("blocks")

            layout_blocks = []
            page_full_text = []

            for idx, block in enumerate(text_blocks):
                x0, y0, x1, y1, b_text, block_no, block_type = block[:7]
                b_text_str = str(b_text).strip()
                if not b_text_str:
                    continue
                
                # Normalize coordinates float [0.0, 1.0]
                norm_bbox = [
                    round(x0 / width, 4) if width > 0 else 0.0,
                    round(y0 / height, 4) if height > 0 else 0.0,
                    round(x1 / width, 4) if width > 0 else 0.0,
                    round(y1 / height, 4) if height > 0 else 0.0
                ]

                layout_blocks.append({
                    "reading_order": idx,
                    "bbox": norm_bbox,
                    "text": b_text_str
                })
                page_full_text.append(b_text_str)

            combined_page_text = "\n".join(page_full_text)

            layout_json_path = page_dir / "layout.json"
            with open(layout_json_path, "w", encoding="utf-8") as f:
                json.dump({
                    "page_number": p_num,
                    "width": width,
                    "height": height,
                    "blocks": layout_blocks
                }, f, indent=2)

            # Classify page & write overview.json
            classification = classify_page_content(combined_page_text)
            is_scanned = classification == "scanned"

            overview_json_path = page_dir / "overview.json"
            with open(overview_json_path, "w", encoding="utf-8") as f:
                json.dump({
                    "page_number": p_num,
                    "is_scanned": is_scanned,
                    "text_character_count": len(combined_page_text),
                    "page_type_classification": classification,
                    "width": width,
                    "height": height
                }, f, indent=2)

            # Record / Update Page in DB
            db_page = db.query(Page).filter(
                Page.document_id == document.id,
                Page.page_number == p_num
            ).first()

            rel_pdf_path = str(page_pdf_path.relative_to(DATA_DIR.parent)) if DATA_DIR.parent in page_pdf_path.parents else str(page_pdf_path)
            rel_png_path = str(page_png_path.relative_to(DATA_DIR.parent)) if DATA_DIR.parent in page_png_path.parents else str(page_png_path)

            if not db_page:
                db_page = Page(
                    id=generate_uuid(),
                    document_id=document.id,
                    page_number=p_num,
                    page_checksum=page_checksum,
                    pdf_artifact_path=rel_pdf_path,
                    image_artifact_path=rel_png_path,
                    page_type_classification=classification,
                    image_path=rel_png_path
                )
                db.add(db_page)
                db.commit()
                db.refresh(db_page)
            else:
                db_page.page_checksum = page_checksum
                db_page.pdf_artifact_path = rel_pdf_path
                db_page.image_artifact_path = rel_png_path
                db_page.page_type_classification = classification
                db_page.image_path = rel_png_path
                db.commit()

            # Clear and record SourceSpans in DB
            db.query(SourceSpan).filter(SourceSpan.page_id == db_page.id).delete()
            for b in layout_blocks:
                span = SourceSpan(
                    id=generate_uuid(),
                    page_id=db_page.id,
                    text_content=b["text"],
                    reading_order=b["reading_order"],
                    bbox_json=json.dumps(b["bbox"]),
                    extraction_metadata_json=json.dumps({"page_number": p_num})
                )
                db.add(span)
            db.commit()

            pages_summary.append({
                "page_number": p_num,
                "checksum": page_checksum,
                "classification": classification,
                "blocks_count": len(layout_blocks)
            })

        # 4. TOC / Bookmarks Indexing
        toc = pdf_doc.get_toc()
        if toc:
            current_chapter = None
            for item in toc:
                level, title, target_page = item[0], item[1], item[2]
                if level == 1:
                    # Chapter
                    chap_no = len(document.chapters) + 1
                    current_chapter = Chapter(
                        id=generate_uuid(),
                        document_id=document.id,
                        chapter_number=chap_no,
                        title=title
                    )
                    db.add(current_chapter)
                    db.commit()
                    db.refresh(current_chapter)
                elif level >= 2 and current_chapter:
                    # Section
                    sec_no = f"{current_chapter.chapter_number}.{len(current_chapter.sections) + 1}"
                    sec = Section(
                        id=generate_uuid(),
                        chapter_id=current_chapter.id,
                        section_number=sec_no,
                        title=title
                    )
                    db.add(sec)
                    db.commit()

        # Save manifest.json
        manifest_path = doc_artifact_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({
                "document_checksum": doc_checksum,
                "source_pdf": pdf_path.name,
                "total_pages": total_pages,
                "processed_pages": target_pages,
                "ingestion_run_id": ingestion_run.id,
                "pages": pages_summary
            }, f, indent=2)

        # Update IngestionRun status to completed
        ingestion_run.status = "completed"
        ingestion_run.completed_at = str(fitz.get_pdf_now() if hasattr(fitz, "get_pdf_now") else "now")
        db.commit()

        pdf_doc.close()
        ingestion_progress_tracker.complete_job()

        return {
            "status": "success",
            "document_id": document.id,
            "document_checksum": doc_checksum,
            "ingestion_run_id": ingestion_run.id,
            "artifact_dir": str(doc_artifact_dir),
            "pages_processed": len(target_pages)
        }
    except Exception as e:
        ingestion_progress_tracker.fail_job(str(e))
        raise e
    finally:
        if should_close_db:
            db.close()

def main():
    default_pdf = SOURCES_DIR / "elementary-algebra-2e_-_WEB.pdf"
    parser = argparse.ArgumentParser(description="Stage 1 PDF Ingestion Pipeline CLI")
    parser.add_argument("--pdf", default=str(default_pdf), help="Path to input PDF document")
    parser.add_argument("--pages", help="Page range filter (e.g., '1-10', '1,2,5')")
    parser.add_argument("--output-dir", help="Base directory for output artifacts")
    parser.add_argument("--reset-db", action="store_true", help="Flush database before ingestion")
    parser.add_argument("--purge-artifacts", action="store_true", help="Purge disk artifacts on database reset")
    
    args = parser.parse_args()

    result = run_stage1_ingestion(
        pdf_path=args.pdf,
        pages_arg=args.pages,
        output_dir=args.output_dir,
        reset_db=args.reset_db,
        purge_artifacts=args.purge_artifacts
    )

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
