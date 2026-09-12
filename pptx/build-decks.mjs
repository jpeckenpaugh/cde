import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = path.resolve(import.meta.dirname, "..");
const deckDir = path.join(workspaceDir, "pptx");
const skillDir = "/Users/jarad/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const runtimePython = "/Users/jarad/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
const stagingDir = path.join(workspaceDir, ".codex-finalizer");
const { resolvePresentationFont, finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools/artifact_tool_utils.mjs")).href);

await fs.mkdir(stagingDir, { recursive: true });
const font = resolvePresentationFont({ fontFamily: "Arial" });
const c = { navy: "#102A43", blue: "#1D4ED8", teal: "#0F766E", ink: "#172033", muted: "#52616B", paper: "#F8FAFC", white: "#FFFFFF" };

function text(slide, value, left, top, width, height, style = {}) {
  const shape = slide.shapes.add({ geometry: "textbox", position: { left, top, width, height }, fill: "none", line: { fill: "none", width: 0 } });
  shape.text = value;
  shape.text.style = { typeface: font, fontSize: 22, color: c.ink, autoFit: "shrinkText", ...style };
  return shape;
}
function base(p, title, subtitle = "") {
  const s = p.slides.add(); s.background.fill = c.paper;
  text(s, title, 72, 36, 1136, 72, { fontSize: 32, bold: true, color: c.navy });
  if (subtitle) text(s, subtitle, 72, 112, 1136, 34, { fontSize: 17, color: c.muted });
  return s;
}
function foot(s, name, page) { text(s, name, 72, 680, 880, 18, { fontSize: 11, color: c.muted }); text(s, String(page), 1160, 680, 48, 18, { fontSize: 11, color: c.muted, align: "right" }); }
function columns(s, aTitle, a, bTitle, b, page, name) {
  text(s, aTitle, 92, 176, 500, 32, { fontSize: 21, bold: true, color: c.blue }); text(s, a, 92, 226, 470, 390, { fontSize: 20 });
  text(s, bTitle, 680, 176, 500, 32, { fontSize: 21, bold: true, color: c.teal }); text(s, b, 680, 226, 470, 390, { fontSize: 20 }); foot(s, name, page);
}
function cover(p, title, subtitle, label) {
  const s = p.slides.add(); s.background.fill = c.navy;
  text(s, title, 100, 180, 1050, 110, { fontSize: 46, bold: true, color: c.white });
  text(s, subtitle, 100, 315, 930, 95, { fontSize: 24, color: "#BFDBFE" });
  text(s, label, 100, 555, 900, 32, { fontSize: 16, color: "#CBD5E1" });
}
function conceptual() {
  const p = Presentation.create({ slideSize: { width: 1280, height: 720 } }); const name = "CDE conceptual overview";
  cover(p, "Compiled Domain Expertise", "A plain-language introduction to a proposal for dependable systems in limited domains", "Conceptual overview");
  let s = base(p, "The question", "How can a computer be dependable inside a clearly limited subject?"); columns(s, "A familiar setting", "Imagine one edition of a textbook, one chapter, its exercises, and its answer key. The scope is deliberate and visible.", "The goal", "Help with questions that belong to that scope. Follow the chapter’s method. Explain the path. Say so when a question goes beyond the chapter.", 2, name);
  s = base(p, "Two kinds of work", "CDE separates preparing knowledge from using it"); columns(s, "Preparation", "People and large language models can read source material, compare answers, propose explanations, and identify recurring reasoning steps. This is exploratory work.", "Execution", "A smaller stored artifact can apply approved steps to supported cases. This is the part intended to be repeatable and inspectable.", 3, name);
  s = base(p, "One small example", "A question can share its structure with many different stories"); columns(s, "Question", "“What is 1 + 2?” has an answer of 3. A teacher may explain it with apples, a number line, or counters.", "Reusable structure", "The story changes. The basic steps remain: identify quantities, combine them, and state the result. CDE calls such reusable steps instructions.", 4, name);
  s = base(p, "What “compiled” means", "Keep the reusable decision structure, not every sentence"); columns(s, "During preparation", "The system gathers candidate explanations and groups similar reasoning steps. A subject expert reviews the result against the chosen source and answer key.", "After preparation", "The artifact retains approved steps and their allowed connections. It does not need the full prose explanation in order to apply the stored structure.", 5, name);
  s = base(p, "What happens when someone asks a question", "The system has three honest outcomes"); columns(s, "Supported question", "It recognizes the needed steps, follows the stored path, gives an answer, and can point to the steps it used.", "Unsupported or unclear question", "It asks for clarification or says that the question falls outside the prepared material. It should not invent a path just to sound helpful.", 6, name);
  s = base(p, "Why the proposal is useful", "The benefit comes from a limited, inspectable scope"); columns(s, "For learners", "A tutoring system could identify the step where an answer diverged from the expected method and offer practice on that specific idea.", "For reviewers", "A policy or procedure tool could show which stored conditions led to a result. That supports checking and revision when source material changes.", 7, name);
  s = base(p, "The hardest problem", "Understanding the question correctly remains essential"); columns(s, "Language varies", "People can ask the same question in many ways. A system must map those variations to the intended stored steps.", "A clear limit", "If that mapping is wrong, a deterministic core can still produce a well-formed result for the wrong interpretation. CDE does not remove this risk.", 8, name);
  s = base(p, "What CDE does and does not claim", "A bounded tool has a bounded promise"); columns(s, "It proposes", "A way to make the execution of a prepared domain more repeatable, attributable, and explicit about its limits.", "It does not propose", "General intelligence, automatic truth, a replacement for expert review, or a reliable answer to every question people may ask.", 9, name);
  s = base(p, "Possible starting points", "The best candidates have a clear source, version, scope, and answer key"); columns(s, "Education", "A textbook chapter, a course module, or a certification unit can provide a fixed body of exercises and expected methods.", "Procedures", "A versioned policy checklist or structured operational process can provide explicit conditions and defined outcomes.", 10, name);
  s = base(p, "The next research question", "Can the interpretation layer be made small and reliable enough for the intended domain?"); text(s, "The proposal stands or falls on evidence: how well can varied human language be mapped to the stored reasoning structure, and how clearly can the system report uncertainty when it cannot?", 150, 245, 980, 150, { fontSize: 28, align: "center" }); foot(s, name, 11);
  return p;
}
function technical() {
  const p = Presentation.create({ slideSize: { width: 1280, height: 720 } }); const name = "CDE technical architecture";
  cover(p, "Compiled Domain Expertise", "Technical architecture, empirical status, and open engineering questions", "Technical architecture deck");
  let s = base(p, "Scope and thesis", "CDE targets bounded, versioned domains rather than open-world intelligence"); columns(s, "Build time", "Use a high-capacity teacher model and a ground-truth corpus to surface candidate reasoning structures, then audit and lower them.", "Runtime", "Execute the surviving structure as a compact, deterministic artifact. The design target is an integer-only CPU runtime with explicit out-of-domain behavior.", 2, name);
  s = base(p, "Five levels", "Keep the theory separate from its first reference implementation"); text(s, "1. CDE: the theory of compiling bounded expertise\n\n2. EKC: the build-time knowledge-compilation method\n\n3. QSBA: the hourglass architecture\n\n4. DIS: the runtime instruction-set artifact\n\n5. QSBC: a C3PA reference implementation", 160, 165, 900, 425, { fontSize: 25 }); foot(s, name, 3);
  s = base(p, "QSBA hourglass", "Language sits at the edges; the domain kernel sits at the waist"); text(s, "Input transduction\nSurface text is mapped to candidate opcodes", 110, 180, 300, 130, { fontSize: 22 }); text(s, "Domain Instruction Set\nDiscrete opcodes, typed relations, and quantized decision weights", 475, 250, 330, 140, { fontSize: 22, bold: true, color: c.navy, align: "center" }); text(s, "Output transduction\nA trace or terminal state is rendered for a user or consuming system", 870, 180, 300, 130, { fontSize: 22 }); text(s, "The kernel’s integrity is conditional on correct input projection.", 270, 500, 740, 34, { fontSize: 19, color: c.muted, align: "center" }); foot(s, name, 4);
  s = base(p, "Domain Instruction Set", "A normalized artifact for explicit execution and attribution"); columns(s, "Stored entities", "Inferences link a canonical input form to a terminal state. Opcodes provide a finite instruction alphabet. An inference-opcode map records active steps.", "Decision layer", "A quantized decision matrix maps active opcodes to terminal states. The kernel can validate a path, correlate similar cases, and discriminate between diverging cases.", 5, name);
  s = base(p, "Build-time pipeline", "The method uses ground truth as compiler input"); text(s, "Closed corpus with answer keys\n\nTeacher rationales and explanations\n\nConcept induction, canonicalization, and pruning\n\nCompilation audits\n\nStatic lowering into a DIS and an extractor", 180, 155, 900, 420, { fontSize: 25, align: "center" }); foot(s, name, 6);
  s = base(p, "Required audits", "The artifact should fail compilation when its structure is weak"); columns(s, "Coverage and concepts", "Vocabulary saturation tests whether new decision-relevant concepts continue to appear. Entropy checks reject trivial label paraphrases. Contrastive weights identify discriminative opcodes.", "Robustness", "Quantization stress tests whether the decision structure survives conversion from soft to discrete activations. Structural checks reject untyped transitions, conflicts, and invalid paths.", 7, name);
  s = base(p, "Reference evidence from QSBC", "The C3PA experiment supports concept compression; it does not solve extraction"); columns(s, "Observed", "Teacher rationales improved the 2,858-sample subset from 0.6559 accuracy to 0.7541. Removing singleton concepts reduced 8,706 concepts to 1,408 with a modest change to 0.7468 accuracy.", "Unresolved", "A naïve linear X-to-concept extractor achieved test Recall@3 of 0.098. Concept-driven classification fell to 0.6135 accuracy, below the concept-blind baseline.", 8, name);
  s = base(p, "Phase 3 extraction", "The input-to-opcode mapping is the central engineering risk"); columns(s, "Feasibility probe", "Train a stronger student model offline to determine whether the desired opcodes can be predicted without exposing terminal labels as a shortcut.", "Static lowering", "Distill the feasible structure into compact mechanisms such as lexical anchors, decision lists, and quantized cascades. The README presents this as a proposed strategy.", 9, name);
  s = base(p, "Integrity boundaries", "Determinism in the core does not prove semantic correctness everywhere"); columns(s, "What the core can establish", "A path can be typed, finite, internally consistent, and exactly attributable once the active opcodes are correct.", "What it cannot establish alone", "Whether a transducer selected the right opcodes, whether the compiled source is complete, or whether the stipulated ground truth remains appropriate after a domain version changes.", 10, name);
  s = base(p, "Deployment targets", "Targets, not demonstrated guarantees"); columns(s, "Target artifact", "Less than 1 MiB total binary, less than 4 MiB dynamic memory, integer-only CPU execution, and an explicit out-of-domain halt.", "Dependency", "These targets depend on a successful static extractor. The decision head is compact; the extractor determines the practical size and latency of the complete system.", 11, name);
  s = base(p, "Research agenda", "The next work should test the claims at the level where they can fail"); text(s, "1. Scale saturation and entropy audits from the subset to the full corpus.\n\n2. Test whether a stronger offline student can recover opcodes robustly.\n\n3. Lower the successful structure into a static extractor.\n\n4. Measure size, latency, coverage, and false-halt behavior on held-out documents.\n\n5. Compare a second bounded domain with a clearer instructional structure.", 140, 155, 1000, 440, { fontSize: 24 }); foot(s, name, 12);
  return p;
}
async function save(presentation, filename) {
  const finalPath = path.join(deckDir, filename); const candidatePath = path.join(stagingDir, `candidate-${filename}`);
  const receiptPath = path.join(stagingDir, `${filename}.validation.json`);
  const stamp = new Date().toISOString().replaceAll(":", "-");
  try { await fs.rename(finalPath, path.join(stagingDir, `${filename}.${stamp}.previous`)); } catch (error) { if (error.code !== "ENOENT") throw error; }
  try { await fs.rename(receiptPath, path.join(stagingDir, `${filename}.${stamp}.previous.validation.json`)); } catch (error) { if (error.code !== "ENOENT") throw error; }
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
  await finalizePresentation({ workspaceDir, candidatePath, finalPath, pythonExecutable: runtimePython, integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"), layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"), layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-bullet-geometry", "--validate-heading-fit"], fontPolicy: { basis: "design", families: [font] }, verifyArtifactToolImport: true, receiptPath });
  console.log(`Created ${finalPath}`);
}
await save(conceptual(), "cde-conceptual-overview.pptx");
await save(technical(), "cde-technical-architecture.pptx");
