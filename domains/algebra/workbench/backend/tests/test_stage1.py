import json
import pytest
from pathlib import Path
import pymupdf as fitz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models.domain  # Ensures models are imported
from app.db.session import Base, get_db
from app.main import app
from app.models.domain import Document, Page, SourceSpan, ParserEnvironment, IngestionRun
from app.services.ingest_stage1 import (
    compute_file_checksum, parse_page_range, run_stage1_ingestion
)

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample_test.pdf"
    doc = fitz.open()
    
    # Page 1: Narrative & TOC
    page1 = doc.new_page(width=600, height=800)
    page1.insert_text((50, 100), "Table of Contents\nChapter 1 Foundations", fontsize=18)
    
    # Page 2: Exercise list
    page2 = doc.new_page(width=600, height=800)
    page2.insert_text((50, 100), "Exercises Section 1.1\n1. Solve for x: 2x + 5 = 9", fontsize=14)
    
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path

def test_parse_page_range():
    assert parse_page_range("1-3,5", 10) == [1, 2, 3, 5]
    assert parse_page_range(None, 5) == [1, 2, 3, 4, 5]
    assert parse_page_range("2", 5) == [2]

def test_compute_file_checksum(sample_pdf):
    checksum = compute_file_checksum(sample_pdf)
    assert isinstance(checksum, str)
    assert len(checksum) == 64

def test_stage1_ingestion_and_endpoints(sample_pdf, tmp_path):
    db = TestingSessionLocal()
    output_dir = tmp_path / "artifacts"
    
    res = run_stage1_ingestion(
        pdf_path=sample_pdf,
        pages_arg="1-2",
        output_dir=output_dir,
        db=db
    )
    
    assert res["status"] == "success"
    doc_checksum = res["document_checksum"]
    doc_id = res["document_id"]
    
    # Verify file artifacts
    page1_dir = output_dir / doc_checksum / "pages" / "page_0001"
    assert (page1_dir / "page.pdf").exists()
    assert (page1_dir / "page.png").exists()
    assert (page1_dir / "layout.json").exists()
    assert (page1_dir / "overview.json").exists()

    with open(page1_dir / "overview.json") as f:
        overview1 = json.load(f)
        assert overview1["page_number"] == 1
        assert overview1["is_scanned"] is False
        assert overview1["page_type_classification"] == "toc"

    with open(page1_dir / "layout.json") as f:
        layout1 = json.load(f)
        assert layout1["page_number"] == 1
        assert len(layout1["blocks"]) > 0
        bbox = layout1["blocks"][0]["bbox"]
        assert len(bbox) == 4
        assert all(0.0 <= val <= 1.0 for val in bbox)

    # Verify DB records
    db_doc = db.query(Document).filter(Document.id == doc_id).first()
    assert db_doc is not None
    assert db_doc.file_checksum == doc_checksum

    db_pages = db.query(Page).filter(Page.document_id == doc_id).all()
    assert len(db_pages) == 2

    env = db.query(ParserEnvironment).first()
    assert env is not None
    assert env.python_version is not None

    run = db.query(IngestionRun).filter(IngestionRun.document_id == doc_id).first()
    assert run is not None
    assert run.status == "completed"

    db.close()

    # Test single page PDF and PNG API endpoints
    pdf_resp = client.get(f"/api/documents/{doc_id}/pages/1/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"

    img_resp = client.get(f"/api/documents/{doc_id}/pages/1/image")
    assert img_resp.status_code == 200
    assert img_resp.headers["content-type"] == "image/png"
