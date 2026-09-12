# Compilation Is Not Generalization

**A boundary document for CDE / EKC pipelines. Read this before designing schemas, prompts, contracts, or evaluations.**

---

## The single distinction

Traditional machine learning learns a function from samples of an unknown distribution. **Compiled Domain Expertise (CDE)** compiles a known, closed, versioned corpus into a static artifact.

These are different computational regimes, and importing assumptions from one into the other corrupts the pipeline. The most common failure mode in agentic sessions is an agent quietly applying ML framing to a CDE/EKC task. This document exists to make that failure detectable and correctable.

If you are designing or contributing to a CDE pipeline, assume **every ML convention is wrong unless explicitly established otherwise.**

---

## The full contrast

| Dimension | Traditional ML | CDE / EKC |
|---|---|---|
| **Task** | Learn \(P(Y \mid X)\) from samples | Compile a corpus into a Domain Instruction Set (DIS) |
| **Data** | A sample drawn from an unknown distribution | The ground truth, closed and versioned |
| **Labels / answer key** | Targets to predict; must not leak | Compiler input; must be visible to the teacher |
| **Leakage** | Fatal | Category error — the answer key *is* the compiler input |
| **Goal** | Generalize to unseen inputs | Recognize variation of known inputs |
| **Success metric** | Held-out accuracy / F1 | Vocabulary saturation, extractor recall, syntactic soundness |
| **Overfitting** | Memorizing training data | Vocabulary bloat — new opcodes appearing as corpus scales |
| **Underfitting** | Too simple, misses signal | Not applicable — incomplete DIS fails loudly |
| **What "generalization" means** | Interpolating to new inputs | (Retired term — see *recognition under variation*) |
| **Runtime artifact** | Trained weights | Sub-megabyte DIS binary |
| **Runtime hardware** | GPU / TPU | Integer CPU |
| **Runtime substrate** | Continuous embeddings, attention | Discrete opcodes, typed relational graph |
| **Runtime process** | Forward pass through neural network | Deterministic program execution |
| **Role of probability** | Central at runtime | Eliminated at runtime; build-time only |
| **Failure mode** | Silent, distributed, plausible | Loud, syntactic, localized |
| **Attribution** | Post-hoc, approximate | Exact by construction |
| **Versioning** | Weights frozen; training stochastic | Entire artifact versioned and deterministic |
| **Reproducibility** | Statistical | Byte-level |
| **Role of the teacher LLM** | The model | Build-time scaffolding + runtime I/O interface |
| **After build** | Teacher *is* the artifact | Teacher discarded; artifact is standalone |
| **What "learning" means** | Gradient descent on loss | Opcode induction + canonicalization |
| **What "inference" means** | Forward pass | Compiled program execution |
| **What "prediction" means** | Sampled distribution output | Deterministic evaluation |
| **What "confidence" means** | Softmax score | Not applicable — output or explicit halt |
| **Evaluation** | Train/val/test split | Compilation audits + surface-variation probe |
| **Out-of-domain** | Low confidence, silent | Explicit loud halt |
| **Interpretability** | Post-hoc | By construction |

---

## Banned terms and their EKC replacements

When writing schemas, prompts, contracts, or documentation for this pipeline, use the right column.

| Do not say | Say instead |
|---|---|
| Train set / test set | Corpus (compiled) / variation probe |
| Train/test split | Compilation boundary |
| Held-out set | Surface-variation set |
| Generalization | Recognition under variation |
| Gold set | Compilation seed batch |
| Leakage | *(not applicable — do not invoke)* |
| Overfitting | Vocabulary bloat |
| Loss | *(not applicable — no gradient descent)* |
| Epoch | Interrogation pass |
| Model | Domain Instruction Set (DIS) |
| Weights | Quantized transition weights (INT8) |
| Inference | Kernel execution |
| Prediction | Terminal state |
| Confidence score | *(not applicable — explicit halt or commit)* |
| Accuracy | Soundness + coverage (report separately) |
| Validation set | Audit batch |

If a term from the left column appears in a design doc, prompt, or schema, it is a signal that ML framing has crept in. Stop and correct it.

---

## What is *not* different

Two things carry over from ML, with renamed vocabulary:

**1. Extractor evaluation.** Once the Phase 3 extractor is built, you evaluate it on inputs it was not trained on. But "not trained on" means *surface variants of the same X* — paraphrases, translations, register shifts — not new X's. The extractor's job is **recognition**, not generalization. Held-out data has the same semantics, only different surface.

**2. Corpus verification.** Answers in the answer key should be verified symbolically or numerically where possible. This is a **soundness check on the corpus**, not a generalization check. It confirms the ground truth is internally consistent before compilation begins.

---

## What the correct pipeline looks like

1. **Ingest** — parse the source, link answers to questions, preserve source spans. Raw extraction is immutable.
2. **Interrogate** — teacher LLM produces C for each (X, Y), with the answer key visible by design.
3. **Induce** — cluster, canonicalize, audit entropy \(H(Y \mid C_k)\), reject label paraphrases.
4. **Saturate** — measure \(\Delta K\) as corpus scales. If vocabulary growth does not decay toward zero, the domain lacks closure — halt and reconsider.
5. **Lower** — compile to DIS: INT8 weights, typed transitions, relational graph.
6. **Probe** — surface-variation test. Same X, different surface. Measure recognition, not generalization.
7. **Deploy** — CPU-only kernel, loud failure on out-of-domain inputs.

Not one of these stages is a training stage. Not one produces or consumes a train/test split. Not one measures generalization.

---

## The four mandatory audits

These replace validation. They are not optional.

- **Vocabulary Saturation** — \(\Delta K_{\text{decision-relevant}}(n) \to 0\) as corpus grows. Tests whether the domain is closed.
- **Concept-Label Entropy** — \(H(Y \mid C_k)\) should be intermediate (roughly 1.0–2.8 bits). Near-zero means the opcode is a disguised label.
- **Quantization Stress** — step activations down through continuous → decile → ternary → binary. If downstream accuracy collapses, the representations were leaking soft information.
- **Contrastive Weight** — shared opcodes active across opposing classes must show opposite weight polarity. Non-discriminating weights are ablated.

If a schema does not have tables for these audits, it is incomplete. If a pipeline does not run them, it is not EKC.

---

## The load-bearing reframe

The teacher sees the answer key because that is what compilation means. The corpus is closed because the domain is versioned. The artifact does not generalize because generalization was never the goal. The system halts loudly because silence is the failure mode it exists to prevent.

CDE is not a better ML pipeline. It is a different computational regime that solves a different class of problem: **given a bounded, versioned, closed corpus of domain expertise, can we compile it into a static, auditable, deterministic instruction set that runs on bare silicon and fails loudly at its boundaries?**

Every design decision should be legible against that question. If a design decision is only legible against "how do we get better accuracy on unseen data," it is the wrong design decision.
