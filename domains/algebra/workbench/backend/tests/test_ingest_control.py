import pytest
import pymupdf as fitz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models.domain  # Ensures models are imported
from app.db.session import Base, get_db
from app.main import app
from app.db.seed import seed_db
from app.models.domain import Document, Page, Chapter, Section, AssessmentItem
from app.services.ingest_stage1 import reset_database, ingestion_progress_tracker

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=5000")
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
    db = TestingSessionLocal()
    seed_db(db)
    app.dependency_overrides[get_db] = override_get_db
    yield
    db.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_list_source_pdfs():
    response = client.get("/api/documents/sources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_ingest_status():
    response = client.get("/api/documents/ingest/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["idle", "running", "completed", "failed"]

def test_reset_database_helper():
    db = TestingSessionLocal()
    assert db.query(Document).count() > 0
    assert db.query(Chapter).count() > 0
    assert db.query(AssessmentItem).count() > 0

    reset_database(db, purge_artifacts=False)

    assert db.query(Document).count() == 0
    assert db.query(Chapter).count() == 0
    assert db.query(AssessmentItem).count() == 0
    assert db.query(Page).count() == 0
    db.close()

def test_trigger_ingest_and_conflict_gating(tmp_path, monkeypatch):
    # Create temp sample PDF
    pdf_path = tmp_path / "test_sample.pdf"
    doc = fitz.open()
    p1 = doc.new_page(width=600, height=800)
    p1.insert_text((50, 100), "Chapter 1 Test Section 1.1", fontsize=14)
    doc.save(str(pdf_path))
    doc.close()

    # Reset progress tracker state to idle
    ingestion_progress_tracker._state["status"] = "idle"

    # Patch SOURCES_DIR in router to tmp_path
    monkeypatch.setattr("app.routers.documents.SOURCES_DIR", tmp_path)

    response = client.post("/api/documents/ingest", json={
        "pdf_filename": "test_sample.pdf",
        "pages_range": "1",
        "reset_db": False
    })
    assert response.status_code == 202
    res_data = response.json()
    assert "message" in res_data

    # Simulate running status for conflict check
    ingestion_progress_tracker._state["status"] = "running"
    conflict_res = client.post("/api/documents/ingest", json={
        "pdf_filename": "test_sample.pdf",
        "pages_range": "1",
        "reset_db": False
    })
    assert conflict_res.status_code == 409
    assert "currently running" in conflict_res.json()["detail"]

    # Reset state back to idle
    ingestion_progress_tracker._state["status"] = "idle"
