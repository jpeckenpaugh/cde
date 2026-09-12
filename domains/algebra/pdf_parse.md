# PDF Ingestion & Entity Mining Pipeline Specification (`pdf_parse.md`)

## 1. Executive Overview & Core Architectural Principles

This document specifies the end-to-end workflow for ingesting raw textbook/statutory PDF documents, extracting spatial evidence, and mining candidate compilation units for **Compiled Domain Expertise (CDE)** and **Empirical Knowledge Compilation (EKC)**.

### Core Principles
1. **Source Immutability:** The original source PDF is strictly immutable raw evidence. It is never modified, mutated, or sliced in place.
2. **Two-Stage Separation:** 
   - **Stage 1:** 100% deterministic Python preparation (layout decomposition, single-page artifact bursting, TOC indexing).
   - **Stage 2:** Non-deterministic AI/ML entity mining operating exclusively over deterministic single-page artifacts.
3. **Single-Page Artifact Unit of Ingestion:** Raw multi-page PDFs are deterministically burst into single-page PDF/PNG artifacts. These single-page artifacts serve as the fast, lightweight point-of-entry for AI models and UI citation viewing.
4. **"A Parser Proposes; a Reviewer Certifies":** All mined entities enter as `candidate` records. Only explicit human review transitions items to `verified` for downstream CDE instruction set compilation.
5. **First-Class Relational Auditability & Co-existing Parse Runs:** Environment details, parser versions, and execution manifests are stored directly in relational database tables. Multiple parser runs co-exist in the database to enable cross-run diffing and benchmark evaluation against historical human certifications.

---

## 2. Two-Stage Pipeline Workflow

```text
                        [ ORIGINAL PDF DOCUMENT ]
               (Immutable Raw Evidence: e.g., 1290 Pages)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: DETERMINISTIC PREPARATION (Python Scripts)             │
│ - Verify SHA-256 checksum & store in `documents`               │
│ - Extract PDF Outlines / Table of Contents -> `chapters`, `sections` │
│ - Burst PDF into single-page bundles (`page.pdf`, `page.png`)    │
│ - Extract text blocks & bounding boxes -> `source_spans`        │
│ - Classify page structural overview ('toc', 'exercise', etc.)    │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                    [ SINGLE-PAGE ARTIFACT BUNDLES ]
                (data/artifacts/{doc_hash}/pages/page_XXXX/)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: NON-DETERMINISTIC ENTITY MINING (AI/ML Tool Sets)      │
│ - Input: `page.pdf`, `page.png`, `layout.json`, `overview.json` │
│ - Target Routing based on page classification                   │
│ - Mine Assessment Items, Multipart Parts (a,b,c), Answer Keys    │
│ - Cross-Page Accumulator: Stitch questions spanning Page N -> N+1│
│ - Create candidate `item_answer_links` with confidence scores    │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                 [ AUDITABLE CANDIDATE ENTITIES IN DB ]
                    (Tagged with `ingestion_run_id`)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│ HUMAN WORKBENCH CERTIFICATION GATE                              │
│ - Human reviewers inspect candidates via inline PDF viewer      │
│ - Review actions: accept, reject, correct, flag ambiguous       │
│ - Certified items transition to `verified` for CDE DIS Export   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Stage 1: Deterministic Preparation & Single-Page Bursting

### 3.1 Document Registration & Environment Capture
1. Compute SHA-256 checksum of raw source PDF.
2. Record `parser_environments` entry capturing Python version, OS, git commit hash, dependency manifest hash, and model checkpoints.
3. Record `ingestion_runs` entry linking `document_id` to `parser_environment_id`.

### 3.2 Single-Page Artifact Directory Layout
Stage 1 derives a structured artifact tree under `data/artifacts/{document_checksum}/`:

```text
data/artifacts/{document_checksum}/
├── source.pdf                           # Immutable raw source file
├── manifest.json                        # Ingestion run inventory & checksum map
└── pages/
    ├── page_0001/
    │   ├── page.pdf                     # Single-page PDF sub-file (~40 KB)
    │   ├── page.png                     # High-res 300 DPI image for UI/Vision
    │   ├── layout.json                  # Bounding boxes [x0, y0, x1, y1], text blocks
    │   └── overview.json                # Structural page classification
    ├── page_0042/
    │   ├── page.pdf
    │   ├── page.png
    │   ├── layout.json
    │   └── overview.json
    └── ...
```

### 3.3 Structural Indexing (Table of Contents Parsing)
Stage 1 parses PDF bookmarks (`/Outlines`) or structural TOC pages to construct `chapters` and `sections` with explicit page ranges (`start_page`, `end_page`). Every physical page automatically inherits its logical textbook section.

---

## 4. Stage 2: Non-Deterministic Entity Mining

### 4.1 Page-Classification Targeted Routing
Workers inspect `overview.json` for each page artifact:
- `exercise_list`: Routed to Question & Multipart Exercise Miner.
- `answer_key`: Routed to Answer Key Label Extractor.
- `narrative`: Routed to Instructional Worked-Example Extractor.
- `index` / `cover`: Skipped to optimize AI token costs.

### 4.2 Cross-Page Span Accumulation (Multipage Items)
To handle items spanning across page breaks (e.g. Exercise 14 starting on Page 82 and ending on Page 83):
1. Parser processes page spans in `reading_order`.
2. If an exercise block does not reach a terminal marker before page end, the accumulator enters a `CONTINUATION_BUFFER` state.
3. The leading spans of Page $N+1$ are appended to the item.
4. Mined items link to multiple spans via the `item_source_spans` junction table.

### 4.3 Answer Key Matching
Answer keys on end-of-chapter or back-of-book pages are parsed into `answer_entries`. Links between assessment items and answer entries are inserted into `item_answer_links` with `current_status = 'candidate'` and an initial `confidence` score.

---

## 5. Relational Database Auditability Schema

```sql
-- 1. Parser Runtime Environment Audit
CREATE TABLE parser_environments (
    id TEXT PRIMARY KEY,
    python_version TEXT NOT NULL,
    git_commit_hash TEXT NOT NULL,
    package_manifest_hash TEXT NOT NULL,
    model_checkpoint_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Ingestion Run Execution
CREATE TABLE ingestion_runs (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    parser_environment_id TEXT NOT NULL REFERENCES parser_environments(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    status TEXT NOT NULL DEFAULT 'running', -- running, completed, failed
    config_json TEXT
);

-- 3. Source Pages & Single-Page PDF Artifacts
CREATE TABLE pages (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    page_checksum TEXT NOT NULL,               -- SHA-256 of page.pdf
    pdf_artifact_path TEXT NOT NULL,         -- Path to single-page PDF
    image_artifact_path TEXT NOT NULL,       -- Path to 300 DPI PNG
    page_type_classification TEXT,           -- toc, narrative, exercise_list, answer_key
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, page_number)
);

-- 4. Source Text Spans & Bounding Boxes
CREATE TABLE source_spans (
    id TEXT PRIMARY KEY,
    page_id TEXT NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    text_content TEXT NOT NULL,
    reading_order INTEGER NOT NULL DEFAULT 0,
    bbox_json TEXT,                          -- {x0, y0, x1, y1}
    extraction_metadata_json TEXT
);

-- 5. Multi-Span Junction Table for Items
CREATE TABLE item_source_spans (
    item_id TEXT NOT NULL REFERENCES assessment_items(id) ON DELETE CASCADE,
    source_span_id TEXT NOT NULL REFERENCES source_spans(id) ON DELETE CASCADE,
    span_order INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (item_id, source_span_id)
);

-- 6. Multi-Span Junction Table for Answers
CREATE TABLE answer_source_spans (
    answer_id TEXT NOT NULL REFERENCES answer_entries(id) ON DELETE CASCADE,
    source_span_id TEXT NOT NULL REFERENCES source_spans(id) ON DELETE CASCADE,
    span_order INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (answer_id, source_span_id)
);
```

---

## 6. Co-Existing Runs & Cross-Run Comparative Analysis

Because every mined entity carries an `ingestion_run_id`, multiple runs (`run_v1`, `run_v2`) co-exist in the database.

### 6.1 Parser Regression & Progress Diffing
SQL queries can directly diff runs to measure extraction quality improvements:
```sql
-- Identify newly discovered items in Parser v2 vs Parser v1
SELECT r2.item_label, r2.content_text
FROM assessment_items r2
WHERE r2.ingestion_run_id = 'run-v2'
  AND r2.item_label NOT IN (
      SELECT item_label FROM assessment_items WHERE ingestion_run_id = 'run-v1'
  );
```

### 6.2 Human Review Preservation & Benchmark Evaluation
- Human certifications are stored as append-only `review_events`.
- Certified items (`verified`, `rejected`, `corrected`) from prior runs serve as the **gold-standard benchmark**.
- New parser versions are automatically evaluated against historical human certifications without discarding prior reviewer work.

---

## 7. Workbench Integration

1. **Fast Citation Rendering:** The UI loads single-page PDF artifacts (`page.pdf` ~40 KB) or page images (`page.png`) instantly when a user clicks a **`📖 Citation Pointer`**.
2. **Review Action:** Human reviewers accept, reject, correct, or flag candidate links.
3. **CDE Export Gating:** `GET /api/export/verified-samples` strictly queries links marked `verified`, outputting certified $(X,Y)$ compilation units for downstream CDE Domain Instruction Set (DIS) compilation.
