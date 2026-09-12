# YODAYAT.md: The YOLO vs. YODAYAT Vibe Coding Dichotomy

## 1. Executive Summary: "Vibe Coding with a Seatbelt"

Contemporary AI-assisted software development is split between two operational philosophies:

* **YOLO Vibe Coding ("You Only Live Once"):** Unconstrained, prompt-and-pray execution. The human inputs natural language prompts; the AI guesses stacks, DB schemas, and paths in a black box. Initial velocity is high, but the system silently drifts into hallucinated technical debt, leaving the human hoping the output is at least 75% of what they expected.
* **YODAYAT Vibe Coding ("You Only Do As You Are Told"):** High-velocity, conversational development **with a seatbelt**. The human developer and AI operate at the speed of thought—brainstorming, evaluating trade-offs, and steering architecture without writing manual code—while enforcing strict intent gating, sub-agent probing, and empirical runtime verification.

---

## 2. The Timeline Retraceability Paradox

> *"You Only Live Once, but your durable artifacts create a timeline-versioned, retraceable history where alternate parallel sub-agent workflows inhabit parallel yet differentiated execution paths."*

In traditional YOLO development, an AI session is ephemeral: if an unguided prompt breaks the codebase, the history is lost in unstructured chat logs.

In **YODAYAT Vibe Coding**:
1. **Human Time is Linear, Artifacts are Immutable:** Human developers live in linear time, but their intent is committed into **durable, versioned artifacts** (`concept.md`, `pdf_parse.md`, database schemas, git commits).
2. **Parallel Differentiated Workflows:** Sub-agents can inhabit parallel, isolated execution branches against the exact same underlying durable substrate. If an experiment fails, the system rolls back to the last certified checkpoint without corrupting the timeline.
3. **Retraceable Provenance:** Every candidate item, code change, and database record links directly to the specific `ingestion_run_id`, specification version, and human verification event that created it.

---

## 3. The 5 Pillars of YODAYAT Vibe Coding

### Pillar 1: Brainstorm at the Speed of Vibe, Execute at the Precision of a Compiler
Developing at the speed of thought does not require sacrificing rigor. Architectural vision is explored fluidly through conversation; implementation is executed deterministically through explicit specifications.

### Pillar 2: Probing & Question Surfacing Before Mutation
No sub-agent or worker tool writes or edits code immediately upon receiving a task. Sub-agents must first:
1. Review specifications and codebase context.
2. Probe for technical ambiguities, edge cases, and dependency choices.
3. Surface open questions and recommendations for human executive review.

### Pillar 3: Three-Tier Chain-of-Command
* **User (Executive / Architect-in-Chief):** Holds intent, sets goals, evaluates trade-offs, and grants final authorization.
* **Parent Agent (Lead Systems Engineer & PM):** Synthesizes specifications, enforces tech stacks, audits sub-agent output, adds technical recommendations, and presents clean decision gates to the User.
* **Sub-Agents (Specialized Execution Engineers):** Operate in isolated contexts focused on specific tasks, probing specs and executing only upon explicit authorization.

### Pillar 4: Empirical Proof Over Optimistic Trust
No feature or refactor is declared complete based on AI self-confidence. A task is finished only when concrete, empirical runtime evidence is gathered: clean Pytest test runs, 0-error TypeScript builds, and verified live server endpoints.

### Pillar 5: Externalized Static Memory
Instead of clogging LLM context windows with long chat transcripts, knowledge is externalized into concise, structured Markdown artifacts (`pdf_parse.md`, `concept.md`, `YODAYAT.md`). Sub-agents read these files on demand, maintaining low-noise, hyper-focused context windows.

---

## 4. Sub-Agent Rules of Engagement (The YODAYAT Protocol)

When a sub-agent is invoked:
1. **READ:** Inspect all relevant specification artifacts (`pdf_parse.md`, `concept.md`, `YODAYAT.md`).
2. **PROBE:** Identify missing information, technical trade-offs, database migration requirements, and edge cases.
3. **REPORT:** Formulate open questions and present recommendations. Do NOT mutate files during the probing phase.
4. **WAIT:** Await explicit user review and authorization.
5. **EXECUTE:** Implement changes cleanly according to approved decisions.
6. **VERIFY:** Gather empirical log/test proof demonstrating 100% clean execution.
