import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Document, Page
from app.config import SOURCES_DIR, ARTIFACTS_DIR, DATA_DIR

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("/{document_id}/pdf")
def get_document_pdf(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    
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
    doc = db.query(Document).filter(Document.id == document_id).first()
    page = db.query(Page).filter(Page.document_id == document_id, Page.page_number == page_num).first()

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
