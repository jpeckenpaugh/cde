# Real PDF Ingestion & Progress Control Specification (`ingest_control.md`)

## 1. Executive Summary & Objective

This specification details the dual execution model for running Stage 1 PDF ingestion against real textbook documents (such as OpenStax *Elementary Algebra 2e*):

1. **Option B (CLI Database Reset & Production Ingestion):** Enhanced CLI command with `--reset-db` and `--pages` flags for headless database clearing and bulk PDF processing.
2. **Option A (FastAPI Background Ingestion & SPA UI Dashboard):** Asynchronous backend API endpoints for launching background ingestion jobs and polling real-time progress, paired with a React SPA UI "Ingest Textbook" modal and live progress bar.

---

## 2. Option B: CLI Database Reset & Production Ingestion

### Requirements
Update `backend/app/services/ingest_stage1.py` to support CLI flags:
- `--pdf <path>`: Path to raw source PDF (default: `domains/algebra/sources/elementary-algebra-2e_-_WEB.pdf`).
- `--reset-db`: Flushes existing mock data from `documents`, `chapters`, `sections`, `pages`, `source_spans`, `assessment_items`, `item_answer_links`, `parser_environments`, and `ingestion_runs`.
- `--pages <range>`: Optional page range (e.g. `1-50` or `all`).

---

## 3. Option A: FastAPI Background Ingestion & Progress Endpoints

### 3.1 Background Ingestion Trigger Endpoint
`POST /api/documents/ingest`
- **Request Payload:**
  ```json
  {
    "pdf_filename": "elementary-algebra-2e_-_WEB.pdf",
    "pages_range": "1-100",
    "reset_db": true
  }
  ```
- **Behavior:**
  - Launches `Stage1IngestionService` as an asynchronous background task (`fastapi.BackgroundTasks`).
  - Returns `202 Accepted` with `ingestion_run_id`.

### 3.2 Ingestion Status Polling Endpoint
`GET /api/documents/ingest/status`
- **Response Payload:**
  ```json
  {
    "run_id": "run-uuid-1234",
    "status": "running",
    "started_at": "2026-09-12T12:50:00Z",
    "completed_at": null,
    "pages_processed": 42,
    "total_pages": 100,
    "current_page_number": 43,
    "current_section_title": "Section 1.2: Use the Language of Algebra",
    "error_message": null
  }
  ```

---

## 4. Option A: React SPA UI Ingestion Dashboard & Progress Bar

### Requirements
1. **Navbar Trigger Button:** Add an **"Ingest PDF"** action button in `Navbar.tsx`.
2. **Ingestion Setup Modal (`IngestModal.tsx`):**
   - File selector / dropdown (detecting PDFs in `domains/algebra/sources/`).
   - Page Range input (`All Pages` or custom range `1-50`).
   - "Reset DB (Clear Mock Seed Data)" checkbox.
   - "Start Ingestion" submit button.
3. **Live Progress Dashboard Bar:**
   - Animated progress bar showing percentage completion (`pages_processed / total_pages`).
   - Stat cards showing `Pages Processed`, `Current Section`, and `Ingestion Status` (`running`, `completed`, `failed`).
   - Automatically refreshes the Corpus Tree hierarchy upon completion!

---

## 5. YODAYAT Protocol & Sub-Agent Mandate

Sub-agents tasked with building this feature MUST:
1. Perform the **YODAYAT Agent Bootstrap Declaration** (Read `YODAYAT.md` & `ingest_control.md`, affirm commitment, state role & task).
2. Review the spec and probe the codebase for technical open questions without writing code.
3. Report open questions and recommendations to the Parent Lead Agent for User review.
