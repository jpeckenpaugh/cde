import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Document
from app.config import SOURCES_DIR

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("/{document_id}/pdf")
def get_document_pdf(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    
    # Try finding PDF in SOURCES_DIR
    pdf_filename = "elementary-algebra-2e_-_WEB.pdf"
    pdf_path = SOURCES_DIR / pdf_filename

    if not pdf_path.exists():
        # Fallback check inside SOURCES_DIR for any PDF
        pdf_files = list(SOURCES_DIR.glob("*.pdf"))
        if pdf_files:
            pdf_path = pdf_files[0]
        else:
            raise HTTPException(status_code=404, detail="PDF source file not found on server.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{pdf_path.name}"'}
    )
