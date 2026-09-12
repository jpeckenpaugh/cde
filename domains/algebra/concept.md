# Algebra EKC Workbench: First Implementation Task

## Purpose

Build a small local application that establishes the human working surface for
Empirical Knowledge Compilation (EKC) in the elementary-algebra domain. The
first version is deliberately **not** a complete PDF parser and it is not a
machine-learning application. It is a trustworthy, inspectable place to store,
review, and certify structured algebra samples before they become inputs to a
Domain Instruction Set (DIS) compilation process.

The application will use mock data at first. This lets us validate the schema,
review workflow, and provenance model independently of the difficult task of
extracting layout, equations, and answer-key references from a 1,290-page PDF.

## First-Task Outcome

Deliver a local SPA + FastAPI + SQLite application that can:

1. Display a small textbook-like hierarchy of chapters and sections.
2. Browse a set of mock algebra questions, including multipart questions.
3. Show a question, its proposed answer, and the source evidence for both.
4. Let a reviewer accept, reject, or correct a question-to-answer link.
5. Record every review decision, without overwriting the original extracted
   candidate data.
6. Filter samples by workflow status and show how many are ready for EKC
   export.

This is an end-to-end vertical slice. It proves that a candidate item can enter
the workbench, be reviewed by a person, and leave as a certified `(X, Y)`
compilation unit.

## Design Principles

- **Source is immutable.** Extracted text, source coordinates, and parser
  candidates are evidence. Human corrections create new assertions; they do
  not erase the evidence that preceded them.
- **A parser proposes; a reviewer certifies.** No candidate question or answer
  link becomes compilation input merely because the parser assigned a high
  confidence.
- **Every decision is traceable.** A user must be able to travel from a
  normalized sample back to its page and source span, and see who made its
  current review decision.
- **No PDF parsing dependency in the first slice.** Mock spans emulate the
  output contract of a future parser. Replacing fixtures with parser output
  must not require a schema rewrite.
- **Only verified samples cross the boundary.** CDE compilation exports use
  samples with explicit `verified` status. Candidates and unresolved items are
  not silently included.

## Proposed Minimal Architecture

```text
Browser SPA
    | JSON API
FastAPI application
    | ORM + migrations
SQLite database (foreign keys and FTS5 enabled)
    |
Mock seed data: document, pages, source spans, questions, answers, reviews
```

The FastAPI service owns all database access. The SPA is responsible for
navigation and review interactions, not business rules. A future command-line
PDF ingestion routine will use the same backend/service layer to insert an
`ingestion_run`, source pages, spans, and candidate entities.

## Minimal Data Model

The first migration should cover the following entities.

| Entity | Responsibility |
| --- | --- |
| `documents` | Source identity: title, edition, file checksum, page count, and license. |
| `pages` | A page number and optional rendered-image reference for a document. |
| `source_spans` | Immutable extraction evidence: text, page, reading order, optional bounding box, extraction metadata. |
| `chapters` / `sections` | Authored textbook hierarchy, each linked to a source span. |
| `assessment_items` | A question, worked example, or Try It prompt; supports item labels, ordering, and parent-child nesting. |
| `assessment_parts` | Optional independently answerable parts of an assessment item. |
| `answer_entries` | An answer-key entry, preserving its printed label and source span. |
| `item_answer_links` | A proposed or accepted link between a prompt/item part and answer entry, with method and confidence. |
| `review_events` | Append-only human review history: action, actor, timestamp, rationale, and affected link. |

The mock data should contain at least one example of each of the following:

- an unambiguous, verified question-answer pair;
- a candidate link awaiting review;
- a multipart exercise with separate answers;
- a rejected or corrected parser candidate;
- a worked example marked as instructional material rather than an assessment
  sample.

## Workflow States

An item-answer link has one current state:

```text
candidate → reviewed → verified
          ↘ rejected
          ↘ needs_resolution
```

`candidate` is parser or seed output. `reviewed` means a person has inspected
it but further confirmation may be needed. `verified` means the link is
eligible for an EKC export. `rejected` retains the candidate and its reason.
`needs_resolution` identifies a known ambiguity, such as an answer-key label
that appears to map to multiple question parts.

The database should retain a review-event history even if a link's current
state changes. Current state can be stored on the link for fast queries, but
the event record is the audit trail.

## Initial User Experience

The SPA needs three views only:

1. **Corpus view** - A chapter/section tree with totals by review state.
2. **Sample detail** - Prompt, answer candidate, source spans, status, and
   review history in one workspace.
3. **Review queue** - Candidate and unresolved links, ordered by confidence or
   source order, with accept, reject, edit, and mark-needs-resolution actions.

For mock spans, the source panel may show page number, extracted text, and a
placeholder page thumbnail. The API contract should already permit page-image
references and bounding boxes so that real PDF overlays can be added later.

## API Slice

The first API can remain small:

```text
GET  /api/chapters
GET  /api/sections/{section_id}/items
GET  /api/items/{item_id}
GET  /api/review-queue
POST /api/links/{link_id}/review
GET  /api/export/verified-samples
```

The review endpoint accepts an action, optional replacement answer target, and
a rationale. The export endpoint is read-only and must query only verified
links, returning stable identifiers plus prompt/answer text and provenance.

## Explicitly Deferred

- Full-PDF parsing and layout heuristics.
- Equation OCR or symbolic normalization.
- Authentication and multi-user conflict handling.
- Teacher-model interrogation, concept induction, opcode generation, and DIS
  lowering.
- A production deployment target.

These are separate concerns. The success criterion for this task is a small,
locally runnable, reviewable corpus workbench whose mock data demonstrates the
correct provenance and certification behavior.

## Acceptance Criteria

- The application starts locally with one documented command or small command
  sequence.
- A fresh SQLite database can be initialized and populated with deterministic
  mock data.
- The UI supports reviewing at least the five mock scenarios named above.
- Every displayed normalized item links back to source-span evidence.
- Review decisions are persisted as append-only events.
- The verified-sample export excludes every non-verified candidate.
- Basic backend tests demonstrate foreign-key integrity, review transitions,
  and export filtering.

## Next Implementation Decision

Choose the frontend baseline: either React + Vite for a conventional SPA or a
minimal static JavaScript client served by FastAPI. React + Vite is preferred
if the workbench is expected to grow into a sustained review tool; the static
client is appropriate only if the first milestone must optimize for the
fewest moving parts.
