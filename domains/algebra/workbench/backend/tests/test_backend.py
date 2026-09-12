import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models.domain  # Ensures models are imported
from app.db.session import Base, get_db
from app.main import app
from app.db.seed import seed_db

# Use StaticPool with sqlite in-memory so all connections share the same in-memory database
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

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_db(db)
    yield
    db.close()
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_get_chapters():
    response = client.get("/api/chapters")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Foundations"
    assert len(data[0]["sections"]) == 2

def test_get_review_queue():
    response = client.get("/api/review-queue")
    assert response.status_code == 200
    data = response.json()
    statuses = {item["current_status"] for item in data}
    assert "candidate" in statuses or "needs_resolution" in statuses
    assert "verified" not in statuses

def test_submit_link_review_accept():
    response = client.post("/api/links/link-q5/review", json={
        "action": "accept",
        "actor": "test_reviewer",
        "rationale": "Looks correct"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == "verified"
    assert len(data["review_events"]) == 1
    assert data["review_events"][0]["action"] == "accept"
    assert data["review_events"][0]["actor"] == "test_reviewer"

def test_submit_link_review_correct():
    response = client.post("/api/links/link-q10b/review", json={
        "action": "correct",
        "actor": "test_reviewer",
        "replacement_answer_id": "ans-q10b",
        "rationale": "Relinked to correct answer key"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == "verified"
    assert data["answer_id"] == "ans-q10b"

def test_export_verified_samples():
    response = client.get("/api/export/verified-samples")
    assert response.status_code == 200
    data = response.json()
    for sample in data:
        assert sample["verification_status"] == "verified"
        assert "provenance" in sample

    exported_link_ids = {sample["link_id"] for sample in data}
    assert "link-q5" not in exported_link_ids

def test_get_document_pdf():
    response = client.get("/api/documents/1/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

