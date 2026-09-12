import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Document, Page
from app.config import SOURCES_DIR, ARTIFACTS_DIR, DATA_DIR
from app.schemas.domain import IngestRequestSchema, IngestStatusResponseSchema, SourcePdfSchema
from app.services.ingest_stage1 import run_stage1_ingestion, ingestion_progress_tracker

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("/sources", response_model=list[SourcePdfSchema])
def list_source_pdfs():
    if not SOURCES_DIR.exists():
        return []
    sources = []
    for pdf_file in SOURCES_DIR.glob("*.pdf"):
        sources.append({
            "filename": pdf_file.name,
            "path": str(pdf_file),
            "size_bytes": pdf_file.stat().st_size
        })
    return sources

def _run_ingest_background(pdf_path: Path, pages_range: str | None, reset_db: bool, purge_artifacts: bool):
    try:
        run_stage1_ingestion(
            pdf_path=pdf_path,
            pages_arg=pages_range,
            reset_db=reset_db,
            purge_artifacts=purge_artifacts
        )
    except Exception as e:
        print(f"Background ingestion failed: {e}")

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
def trigger_document_ingestion(payload: IngestRequestSchema, background_tasks: BackgroundTasks):
    if ingestion_progress_tracker.is_running():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An ingestion job is currently running."
        )

    pdf_path = SOURCES_DIR / payload.pdf_filename
    if not pdf_path.exists():
        pdf_files = list(SOURCES_DIR.glob("*.pdf"))
        if pdf_files:
            pdf_path = pdf_files[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source PDF '{payload.pdf_filename}' not found in {SOURCES_DIR}"
            )

    background_tasks.add_task(
        _run_ingest_background,
        pdf_path=pdf_path,
        pages_range=payload.pages_range,
        reset_db=payload.reset_db,
        purge_artifacts=payload.purge_artifacts
    )

    return {
        "message": "Ingestion job started in background.",
        "pdf_filename": pdf_path.name,
        "pages_range": payload.pages_range,
        "reset_db": payload.reset_db
    }

@router.get("/ingest/status", response_model=IngestStatusResponseSchema)
def get_ingestion_status():
    return ingestion_progress_tracker.get_status()

@router.get("/active/info")
@router.get("/{document_id}/info")
def get_document_info(document_id: str = "active", db: Session = Depends(get_db)):
    if document_id == "active" or document_id == "1":
        doc = db.query(Document).first()
    else:
        doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        doc = db.query(Document).first()

    if not doc:
        return {
            "id": "1",
            "title": "No Document Ingested",
            "ingested_pages_count": 0,
            "ingested_pages": [],
            "total_pages": 0
        }

    pages = db.query(Page).filter(Page.document_id == doc.id).order_by(Page.page_number).all()
    ingested_page_numbers = sorted(list(set(p.page_number for p in pages)))

    return {
        "id": doc.id,
        "title": doc.title,
        "file_checksum": doc.file_checksum,
        "ingested_pages_count": len(ingested_page_numbers),
        "ingested_pages": ingested_page_numbers,
        "total_pages": doc.page_count or len(ingested_page_numbers)
    }

@router.get("/{document_id}/pdf")
def get_document_pdf(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        doc = db.query(Document).first()

    # Try finding PDF in SOURCES_DIR
    pdf_filename = "elementary-algebra-2e_-_WEB.pdf"
    pdf_path = SOURCES_DIR / pdf_filename

    if not pdf_path.exists():
        pdf_files = list(SOURCES_DIR.glob("*.pdf"))
        if pdf_files:
            pdf_path = pdf_files[0]
        elif doc and doc.file_checksum:
            artifact_pdf = ARTIFACTS_DIR / doc.file_checksum / "source.pdf"
            if artifact_pdf.exists():
                pdf_path = artifact_pdf
            else:
                raise HTTPException(status_code=404, detail="PDF source file not found on server.")
        else:
            raise HTTPException(status_code=404, detail="PDF source file not found on server.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{pdf_path.name}"'}
    )

@router.get("/{document_id}/pages/{page_num}/pdf")
def get_single_page_pdf(document_id: str, page_num: int, db: Session = Depends(get_db)):
    if document_id == "active" or document_id == "1":
        doc = db.query(Document).first()
    else:
        doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        doc = db.query(Document).first()

    doc_id = doc.id if doc else document_id
    page = db.query(Page).filter(Page.document_id == doc_id, Page.page_number == page_num).first()

    pdf_file_path = None
    if page and page.pdf_artifact_path:
        candidate = Path(page.pdf_artifact_path)
        if candidate.is_absolute() and candidate.exists():
            pdf_file_path = candidate
        else:
            candidate_rel = DATA_DIR.parent / page.pdf_artifact_path
            if candidate_rel.exists():
                pdf_file_path = candidate_rel

    if not pdf_file_path and doc and doc.file_checksum:
        fallback = ARTIFACTS_DIR / doc.file_checksum / "pages" / f"page_{page_num:04d}" / "page.pdf"
        if fallback.exists():
            pdf_file_path = fallback

    if not pdf_file_path or not pdf_file_path.exists():
        raise HTTPException(status_code=404, detail=f"Single-page PDF for page {page_num} not found.")

    return FileResponse(
        path=pdf_file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="page_{page_num:04d}.pdf"'}
    )

@router.get("/{document_id}/pages/{page_num}/image")
def get_single_page_image(document_id: str, page_num: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    page = db.query(Page).filter(Page.document_id == document_id, Page.page_number == page_num).first()

    img_file_path = None
    if page and page.image_artifact_path:
        candidate = Path(page.image_artifact_path)
        if candidate.is_absolute() and candidate.exists():
            img_file_path = candidate
        else:
            candidate_rel = DATA_DIR.parent / page.image_artifact_path
            if candidate_rel.exists():
                img_file_path = candidate_rel
    elif page and page.image_path:
        candidate = Path(page.image_path)
        if candidate.is_absolute() and candidate.exists():
            img_file_path = candidate
        else:
            candidate_rel = DATA_DIR.parent / page.image_path
            if candidate_rel.exists():
                img_file_path = candidate_rel

    if not img_file_path and doc and doc.file_checksum:
        fallback = ARTIFACTS_DIR / doc.file_checksum / "pages" / f"page_{page_num:04d}" / "page.png"
        if fallback.exists():
            img_file_path = fallback

    if not img_file_path or not img_file_path.exists():
        raise HTTPException(status_code=404, detail=f"Single-page PNG image for page {page_num} not found.")

    return FileResponse(
        path=img_file_path,
        media_type="image/png"
    )
