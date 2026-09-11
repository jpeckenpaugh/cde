import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_presentation(filename="compiled_domain_expertise.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    DARK_NAVY = RGBColor(15, 23, 42)     # #0F172A
    SLATE_GRAY = RGBColor(71, 85, 105)   # #475569
    TEXT_BLACK = RGBColor(30, 41, 59)    # #1E293B
    TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
    PRIMARY_BLUE = RGBColor(37, 99, 235) # #2563EB
    ACCENT_TEAL = RGBColor(13, 148, 136) # #0D9488
    BG_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC
    CARD_BG = RGBColor(255, 255, 255)
    BORDER_COLOR = RGBColor(226, 232, 240)
    ALERT_RED = RGBColor(225, 29, 72)
    SUCCESS_GREEN = RGBColor(22, 163, 74)

    blank_layout = prs.slide_layouts[6]

    def add_base_slide(title_text, subtitle_text=""):
        slide = prs.slides.add_slide(blank_layout)
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_LIGHT
        bg.line.fill.background()

        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial"
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = DARK_NAVY

        if subtitle_text:
            p2 = tf.add_paragraph()
            p2.text = subtitle_text
            p2.font.name = "Arial"
            p2.font.size = Pt(13)
            p2.font.color.rgb = SLATE_GRAY
            p2.space_before = Pt(4)

        return slide

    def set_speaker_note(slide, note_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = note_text

    def add_card(slide, left, top, width, height, title="", title_color=PRIMARY_BLUE, bg_color=CARD_BG, border_color=BORDER_COLOR):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()

        tx_box = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = tx_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        if title:
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = "Arial"
            p.font.size = Pt(15)
            p.font.bold = True
            p.font.color.rgb = title_color
            p.space_after = Pt(8)

        return tf

    # SLIDE 1: Title
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = DARK_NAVY
    bg1.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "COMPILED DOMAIN EXPERTISE"
    p.font.name = "Arial"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    p_sub = tf1.add_paragraph()
    p_sub.text = "The Quantized Semantic Bottleneck Architecture (QSBA) & Domain Instruction Sets"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = RGBColor(147, 197, 253)
    p_sub.space_before = Pt(14)

    p_meta = tf1.add_paragraph()
    p_meta.text = "Severing Knowledge Acquisition from Knowledge Execution for Deterministic Verification"
    p_meta.font.name = "Arial"
    p_meta.font.size = Pt(14)
    p_meta.font.color.rgb = RGBColor(203, 213, 225)
    p_meta.space_before = Pt(24)

    set_speaker_note(s1, "Welcome. Today we present Compiled Domain Expertise (CDE). We address the core vulnerabilities of frontier AI—probabilistic drift, parameter bloat, and unverifiable reasoning—by compiling bounded human expertise into static, deterministic, CPU-executable instruction sets.")

    # SLIDE 2: The Substrate - Tokens
    s2 = add_base_slide("Slide 1: The Substrate — Tokens and Giant Vocabularies", "Frontier LLMs operate over high-dimensional continuous manifolds")
    tf2_a = add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Tokenization & Vocabulary Penalty", PRIMARY_BLUE)
    bullets2_a = [
        "Arbitrary Tokenization: Words and subwords are encoded into arbitrary integer token IDs.",
        "Massive Global Search Space: At every step, operations compute across 50,000 to 100,000+ token vocabularies.",
        "Input Projection Burden: Every human prompt must be projected across dense, continuous embedding spaces before reasoning begins."
    ]
    for b in bullets2_a:
        p = tf2_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf2_b = add_card(s2, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Open-World Dilemma", SLATE_GRAY)
    bullets2_b = [
        "Unbounded Knowledge Scope: The model ingests open-domain web data, mixing verified logic with unverified prose.",
        "No Architectural Separation: Computational logic and linguistic phrasing occupy the exact same floating-point substrate.",
        "Inherited Ambiguity: Because the model's atomic unit is a text fragment rather than a verified domain state, ambiguity enters at step zero."
    ]
    for b in bullets2_b:
        p = tf2_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s2, "Because the substrate operates over raw language tokens rather than domain states, every downstream operation inherits open-world ambiguity and continuous floating-point overhead.")

    # SLIDE 3: Probabilistic Prediction
    s3 = add_base_slide("Slide 2: The Mechanism — Probabilistic Token Prediction", "P(Token_{t+1} | Context): Likelihood is not truth")
    tf3_a = add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Statistical Plausibility", PRIMARY_BLUE)
    bullets3_a = [
        "Surface Emulation: Models generate what is statistically likely based on pretraining distributions, not what is logically necessary.",
        "No Grounding Gate: The neural architecture lacks native logic gates to evaluate True vs. False or Reality vs. Hallucination.",
        "Continuous Manifold Drift: Minor perturbations in input prompts cause unpredictable shifts across high-dimensional latent space."
    ]
    for b in bullets3_a:
        p = tf3_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf3_b = add_card(s3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Inherent Veracity Blindspots", ALERT_RED)
    bullets3_b = [
        "Circular Logic & Paradoxes: Models routinely assert contradictions (C and not-C) if the phrasing sounds contextually authoritative.",
        "Global Pull Penalty: Sampling from a global dictionary exposes every query to out-of-domain drift and inappropriate associations.",
        "Silent Failures: The model produces plausible, polished explanations even when the underlying factual derivation is broken."
    ]
    for b in bullets3_b:
        p = tf3_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s3, "Output generation is governed entirely by likelihood. The model lacks any built-in mechanism to distinguish truth from plausible falsehood.")

    # SLIDE 4: Chain of Thought
    s4 = add_base_slide("Slide 3: The Band-Aid — Chain of Thought (CoT)", "Simulating deliberation through intermediate token generation")
    tf4_a = add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Concept of CoT", PRIMARY_BLUE)
    bullets4_a = [
        "Stopping to 'Think': Prompting or training models to emit an intermediate token stream before emitting the final answer.",
        "Simulated Deliberation: Emulates step-by-step human work, planning, and scratchpad arithmetic.",
        "Working Context Extension: Intermediate tokens provide richer self-attention context, nudging the probability curve toward better answers."
    ]
    for b in bullets4_a:
        p = tf4_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf4_b = add_card(s4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Mechanical Reality", SLATE_GRAY)
    bullets4_b = [
        "Tokens, Not Thoughts: The intermediate stream does not represent conscious reasoning; it is just another autoregressive token sequence.",
        "No Hardware Anchor: The scratchpad steps are generated on the exact same stochastic floating-point substrate as the final output.",
        "Compute Multiplication: Emitting 500 'thinking' tokens multiplies runtime latency, cloud GPU costs, and memory footprints."
    ]
    for b in bullets4_b:
        p = tf4_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s4, "CoT feels like deliberate human reasoning, but under the hood, it is simply more probabilistic tokens generated on the same ungrounded substrate.")

    # SLIDE 5: Problems with CoT
    s5 = add_base_slide("Slide 4: The CoT Breakdown — Inherited Probabilistic Debt", "Compounding errors and the illusion of verification")
    tf5_a = add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Compounding Drift", ALERT_RED)
    bullets5_a = [
        "No Ground Truth Gate: There is still no internal arbiter to determine if an intermediate thought is correct, irrelevant, or hallucinatory.",
        "Error Amplification: If step 3 of a 10-step chain introduces an invalid premise, subsequent tokens plausibly rationalize the false premise rather than correcting it.",
        "Stochastic Fragility: The reasoning chain is highly sensitive to token sampling temperature and minor prompt variations."
    ]
    for b in bullets5_a:
        p = tf5_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf5_b = add_card(s5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Epistemic Illusion", SLATE_GRAY)
    bullets5_b = [
        "Right Answer, Wrong Work: Models frequently arrive at correct final answers via invalid, paradoxical, or hallucinatory derivations.",
        "Rationalization Engine: The model justifies its output post-hoc, masking broken reasoning behind polished, confident prose.",
        "The Core Deficiency: More tokens cannot solve the absence of an external, inspectable ground-truth anchor."
    ]
    for b in bullets5_b:
        p = tf5_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s5, "CoT does not escape the probabilistic stack. When intermediate steps drift, the model simply rationalizes the mistake.")

    # SLIDE 6: Policing Thoughts - The Dead End
    s6 = add_base_slide("Slide 5: The Dead-End — Policing Probability with Probability", "The verification trap: 'Who verifies the verifier?'")
    tf6_a = add_card(s6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Multi-Agent Supervisor Loop", PRIMARY_BLUE)
    bullets6_a = [
        "The Watchdog Pattern: Deploying secondary 'judge' or 'critic' LLMs to scan the CoT and output tokens of the primary model.",
        "Trigger Scanning: Inspecting streams for triggers like 'harmful', 'illogical', 'false', or 'unsupported premise'.",
        "Recursive Agent Hierarchies: Layering reviewers on top of implementers, and auditors on top of reviewers."
    ]
    for b in bullets6_a:
        p = tf6_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf6_b = add_card(s6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Fundamental Dead-End", ALERT_RED)
    bullets6_b = [
        "Probability Policing Probability: The supervisor model is subject to the exact same failure modes as the generator.",
        "Agreement is Not Proof: Two probabilistic systems agreeing is merely evidence of shared training priors—it is not deterministic proof.",
        "The Infinite Regress: Who audits the auditor? Moving uncertainty in a circle does not remove uncertainty."
    ]
    for b in bullets6_b:
        p = tf6_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s6, "Layering agents simply moves uncertainty in a circle. To achieve deterministic integrity, verification cannot rely on continuous neural inference at runtime.")

    # SLIDE 7: The Mathbook Baseline
    s7 = add_base_slide("Slide 6: The Grounding Baseline — The Arithmetic Mathbook", "A simplified model of a closed knowledge domain")
    tf7_a = add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Closed by Construction", PRIMARY_BLUE)
    bullets7_a = [
        "A Deliberately Bounded Universe: Consider a 3rd-grade arithmetic textbook. Its scope is completely fixed by its table of contents.",
        "No Open-World Bleed: It does not contain calculus, quantum mechanics, or internet opinions. Boundaries are explicit.",
        "Finite Operational Vocabulary: Solving every problem in the book requires only a tiny, discrete set of operations: +, -, x, /."
    ]
    for b in bullets7_a:
        p = tf7_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf7_b = add_card(s7, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Answer Keys as Formal Specification", ACCENT_TEAL)
    bullets7_b = [
        "Reframing 'Data Leakage': In traditional ML, exposing the answer key is leakage. In domain compilation, the Teacher's Edition (X, Y) is the exact specification.",
        "Stipulated Ground Truth: Truth is not an ungrounded metaphysical question; it is stipulated by the versioned textbook edition.",
        "Deterministic Expectation: We demand that the system execute arithmetic with exact procedural precision, not statistical guessing."
    ]
    for b in bullets7_b:
        p = tf7_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s7, "When we want reliability, we don't start with the open web. We start with a bounded domain. An arithmetic textbook has fixed rules, a tiny set of operations, and an explicit answer key.")

    # SLIDE 8: Attestations (1+1=2)
    s8 = add_base_slide("Slide 7: Chapter 1, Unit 1, Question 1 — The Attestation", "Defining X (Question) -> Y (Answer) and the attestation atom")
    tf8_a = add_card(s8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Attestation Atom", PRIMARY_BLUE)
    bullets8_a = [
        "The Primary Pair (X -> Y): An input state X paired with an asserted terminal state Y.",
        "X (Input Question): 'What is 1 + 1?'",
        "Y (Terminal State): '2'",
        "The Attestation: The formal binding of (1 + 1 -> 2) within the domain."
    ]
    for b in bullets8_a:
        p = tf8_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf8_b = add_card(s8, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "True vs. False Attestations", SLATE_GRAY)
    bullets8_b = [
        "True Attestation: (1 + 1 -> 2) is validated directly against the Chapter 1 Teacher Answer Key.",
        "False Attestations: (1 + 1 -> 3) or (1 + 1 -> 1) are explicitly invalid state assertions.",
        "Stipulated Validity: (1 + 1 -> 2) is true within this system because the versioned textbook explicitly stipulates it as true.",
        "Beyond Flashcards: Memorizing (X, Y) is not enough. We must extract the intermediate layer: C (Reasoning)."
    ]
    for b in bullets8_b:
        p = tf8_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s8, "We define an Attestation as the pairing of an input X to an output Y. '1 + 1 = 2' is a True Attestation because the textbook's answer key asserts it. But we need C, the reasoning, to understand how it works.")

    # SLIDE 9: Reasoning -> Thoughts -> Ideas
    s9 = add_base_slide("Slide 8: Under the Hood of 1 + 1 = 2 — Reasoning, Thoughts, Ideas", "Deconstructing C into reusable structural primitives")
    tf9_a = add_card(s9, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), "C: Reasoning (Narrative)", SLATE_GRAY)
    bullets9_a = [
        "Raw Teacher Explanation: 'You place one apple on a table. You add another apple next to it. Counting them together gives two.'",
        "Contextual & Wordy: Specific to apples, tables, and narrative style."
    ]
    for b in bullets9_a:
        p = tf9_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(8)

    tf9_b = add_card(s9, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), "Thoughts (Atomic Steps)", PRIMARY_BLUE)
    bullets9_b = [
        "Thought 1: Identify initial unit quantity (1).",
        "Thought 2: Identify incoming unit quantity (1).",
        "Thought 3: Combine both units into a set.",
        "Thought 4: Count elements to determine set cardinality (2)."
    ]
    for b in bullets9_b:
        p = tf9_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(8)

    tf9_c = add_card(s9, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.8), "Ideas (Canonical Opcodes)", ACCENT_TEAL)
    bullets9_c = [
        "Idea A: MAP_INTEGER_TO_SET (Establishing cardinality).",
        "Idea B: INCREMENT_BY_UNIT (Applying additive successor).",
        "Idea C: ASSERT_EQUALITY (Binding count to terminal symbol)."
    ]
    for b in bullets9_c:
        p = tf9_c.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(8)

    set_speaker_note(s9, "Reasoning is the wordy story. Thoughts are the atomic sequential steps. Ideas are the generalized, reusable mathematical primitives that will become our opcodes.")

    # SLIDE 10: 1+2=3 Invariance
    s10 = add_base_slide("Slide 9: Chapter 1, Question 2: 1 + 2 = 3 — Invariance Under Variation", "Surface stories change; underlying Ideas remain invariant")
    tf10_a = add_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Surface Variation (X2 -> Y2)", SLATE_GRAY)
    bullets10_a = [
        "New Problem: 'What is 1 + 2?' -> '3' (True Attestation).",
        "A Completely Different Story: 'Start at point 1 on a number line. Take two hops of one unit to the right. You land on 3.'",
        "Unique Thoughts: Hop 1 (1 -> 2), Hop 2 (2 -> 3), Register position 3.",
        "Linguistic Shift: Moves from physical apples to spatial movement on a line."
    ]
    for b in bullets10_a:
        p = tf10_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf10_b = add_card(s10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Locking into the Same Ideas", SUCCESS_GREEN)
    bullets10_b = [
        "Zero New Concepts: Despite the change in story, it boils down to the exact same Ideas from Question 1:",
        "• Idea A: SET_ORIGIN / MAP_INTEGER_TO_SET",
        "• Idea B: INCREMENT_BY_UNIT (Executed twice)",
        "• Idea C: ASSERT_EQUALITY",
        "Rapid Stabilization: The number of wordy thoughts grows, but the discovery of new Ideas quickly drops toward zero."
    ]
    for b in bullets10_b:
        p = tf10_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s10, "A teacher might explain 1 + 2 using a number line instead of apples. But when boiled down, you don't discover a new universe of math—you lock into the exact same Ideas.")

    # SLIDE 11: 2-1=1 Contrast
    s11 = add_base_slide("Slide 10: Chapter 1, Question 3: 2 - 1 = 1 — Introducing Contrast", "Reusing shared foundations while inducing the inverse operator")
    tf11_a = add_card(s11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Subtraction Attestation", SLATE_GRAY)
    bullets11_a = [
        "New Problem: 'What is 2 - 1?' -> '1' (True Attestation).",
        "The Narrative: 'Two cookies on a plate. You give one cookie away. One cookie remains.'",
        "Intermediate Thoughts: Identify start (2), recognize minus sign as removal, remove 1 item, evaluate remainder (1)."
    ]
    for b in bullets11_a:
        p = tf11_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf11_b = add_card(s11, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Foundations Reused, Inverse Induced", PRIMARY_BLUE)
    bullets11_b = [
        "Reusing Shared Foundations: Idea A (Cardinality) and Idea C (Equality Assertion) are reused unchanged.",
        "One New Idea Induced: Idea D: DECREMENT_BY_UNIT (Inverse successor operator).",
        "Architectural Composition: In three questions, addition and subtraction are captured with just four canonical Ideas."
    ]
    for b in bullets11_b:
        p = tf11_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s11, "Question 3 introduces subtraction. We reuse initial cardinality and equality assertion from earlier problems, inducing just one new Idea: DECREMENT. Our Idea vocabulary is controlled.")

    # SLIDE 12: EKC Build Time
    s12 = add_base_slide("Slide 11: The Build-Time Engine — Empirical Knowledge Compilation", "Offline teacher interrogation across closed domain context")
    tf12_a = add_card(s12, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Offline Compilation Protocol", PRIMARY_BLUE)
    bullets12_a = [
        "The LLM as Compiler: The frontier model is deployed offline in the factory, never to end-users at runtime.",
        "Three Build-Time Inputs: (1) Chapter 1 Full Text Context, (2) Question X, (3) Candidate Y (both True and False answers).",
        "Directive: 'Grounding yourself strictly in Chapter 1, show your complete work in justifying or refuting why X yields Y.'"
    ]
    for b in bullets12_a:
        p = tf12_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf12_b = add_card(s12, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "The 3-Step Lowering Pipeline", ACCENT_TEAL)
    bullets12_b = [
        "1. Capture Reasoning (C): Save the raw generative CoT trace as an introspective rationale.",
        "2. Deconstruct into Thoughts: Segment the narrative into atomic, ordered sequential steps.",
        "3. Canonicalize into Ideas: Index and deduplicate each thought to its underlying invariant opcode.",
        "From Fluff to Structure: Messy neural generation crystallizes into an explicit relational database."
    ]
    for b in bullets12_b:
        p = tf12_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s12, "Empirical Knowledge Compilation uses high-capacity models offline. We feed the chapter context and answer keys, extract the CoT, and lower it into a clean relational database.")

    # SLIDE 13: Relational Schema
    s13 = add_base_slide("Slide 12: From Neural Traces to Bare-Metal Tables — The Relational Schema", "Normalized lookup tables replace continuous probability")
    tf13_a = add_card(s13, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.8), "QUESTIONS (X)", SLATE_GRAY)
    bullets13_a = ["id (PK)", "text ('1 + 1')", "chapter_ref", "Stores invariant problem specs"]
    for b in bullets13_a:
        p = tf13_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(8)

    tf13_b = add_card(s13, Inches(3.8), Inches(1.8), Inches(2.7), Inches(4.8), "REASONINGS (C)", PRIMARY_BLUE)
    bullets13_b = ["id (PK)", "question_id (FK)", "terminal_y ('2')", "type (TRUE/FALSE)", "Derivation tree"]
    for b in bullets13_b:
        p = tf13_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(8)

    tf13_c = add_card(s13, Inches(6.8), Inches(1.8), Inches(2.7), Inches(4.8), "THOUGHTS", SLATE_GRAY)
    bullets13_c = ["id (PK)", "reasoning_id (FK)", "sequence_order", "idea_id (FK)", "Normalized steps"]
    for b in bullets13_c:
        p = tf13_c.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(8)

    tf13_d = add_card(s13, Inches(9.8), Inches(1.8), Inches(2.7), Inches(4.8), "IDEAS (Opcodes)", SUCCESS_GREEN)
    bullets13_d = ["id (PK)", "opcode_mnemonic", "description", "SET_CARDINALITY", "INCREMENT_UNIT"]
    for b in bullets13_d:
        p = tf13_d.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(8)

    set_speaker_note(s13, "Look at what happened: continuous neural tokens crystallized into a normalized SQL database. When you audit why 1 + 1 = 2, you run a SQL join. We have exited the probabilistic stack.")

    # SLIDE 14: Scaling to Textbook & QSBA
    s14 = add_base_slide("Slide 13: The Finite Horizon — Quantized Semantic Bottleneck Architecture", "Scaling across the entire textbook with an explicit hard boundary")
    tf14_a = add_card(s14, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Exhaustive Compilation & Hard Stop", PRIMARY_BLUE)
    bullets14_a = [
        "Scaling Across Chapters: Repeat EKC for all Chapters, Units, and Exercises across the entire textbook.",
        "The Explicit Hard Boundary: Compilation stops strictly at the final page of this textbook edition.",
        "No Web Crawling: The system does not ingest outside math or internet noise. If it is not in the book, it does not exist in the database."
    ]
    for b in bullets14_a:
        p = tf14_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf14_b = add_card(s14, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Bottleneck Defines Scope", ACCENT_TEAL)
    bullets14_b = [
        "In-Scope vs. Out-of-Scope: The populated tables define 100% of the domain universe.",
        "The Quantized Semantic Bottleneck: Natural language must pass through this discrete, audited relational gate.",
        "Vocabulary Saturation: Across hundreds of problems, the discovery rate of new Ideas reaches zero. The instruction set closes."
    ]
    for b in bullets14_b:
        p = tf14_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s14, "We compile the entire textbook, but make a deliberate hard stop at its final page. This discrete set of tables is the Quantized Semantic Bottleneck. Anything within is verified; anything outside is halted.")

    # SLIDE 15: Lowering to DIS Binary
    s15 = add_base_slide("Slide 14: Lowering to Bare Metal — The Domain Instruction Set (DIS)", "Compiling Ideas into a sub-megabyte, CPU-executable binary")
    tf15_a = add_card(s15, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Ideas Lowered to Machine Code", PRIMARY_BLUE)
    bullets15_a = [
        "The Software Compilation Analogy: Just as C code compiles to x86 or ARM assembly, Ideas compile to a Domain Instruction Set (DIS).",
        "Ideas Become Opcodes: SET_ORIGIN, OP_INC, OP_DEC, OP_ASSERT.",
        "Zero English at Runtime: Natural language is stripped away. The binary contains only discrete integer opcodes and relational transition rules."
    ]
    for b in bullets15_a:
        p = tf15_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf15_b = add_card(s15, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Bare-Metal Edge Performance", SUCCESS_GREEN)
    bullets15_b = [
        "Sub-Megabyte Footprint: Total deployable binary target < 1.0 MiB. Dynamic RAM < 4.0 MiB.",
        "Microsecond Execution: Evaluates queries in < 50 microseconds on standard, inexpensive CPUs.",
        "Zero Cloud Dependency: Runs locally on embedded chips or cheap student tablets without GPUs or internet connections."
    ]
    for b in bullets15_b:
        p = tf15_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s15, "We lower our tables into a Domain Instruction Set binary. Every Idea becomes an opcode. It fits in less than 1 megabyte and runs on bare-metal CPUs in microseconds.")

    # SLIDE 16: Interface & Generative Upscaling
    s16 = add_base_slide("Slide 15: The Interface — Putting the LLM Where It Shines", "Language at the edges, logic at the core: Generative Upscaling")
    tf16_a = add_card(s16, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Division of Labor", PRIMARY_BLUE)
    bullets16_a = [
        "Promoting the LLM to Interface: LLMs struggle as bare logic calculators, but excel as translation and rendering interfaces.",
        "Top Bulb (Ingestion): Translates casual student questions ('I have a nickel and find two pennies...') into exact opcode queries.",
        "Thin Waist (DIS): The deterministic binary verifies and executes the mathematical transition with 100% certainty."
    ]
    for b in bullets16_a:
        p = tf16_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf16_b = add_card(s16, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Generative Upscaling (Bottom Bulb)", ACCENT_TEAL)
    bullets16_b = [
        "Upscaling Analog: Like upscaling low-res pixels to 4K, the LLM takes a sparse, proven opcode trace and re-hydrates it into rich natural language.",
        "Beyond Lossy Compression: The structural invariant is preserved with 100% fidelity. The LLM can generate infinite creative variations:",
        "• 'Add 2 apples and 1 apple...'",
        "• 'Add 1 puppy and 1 kitten...'",
        "• 'You + Me = How many people?'"
    ]
    for b in bullets16_b:
        p = tf16_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s16, "We don't throw the LLM away. It translates student questions at the top, and at the bottom, it upscales verified opcode traces into rich, engaging explanations.")

    # SLIDE 17: 10-Year-Old Meets Frontier LLM
    s17 = add_base_slide("Slide 16: The Reality Check — A 10-Year-Old Meets a Frontier LLM", "'I need to study math. Can you help me?' — The Failure Modes")
    tf17_a = add_card(s17, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Infrastructure & Safety Liabilities", ALERT_RED)
    bullets17_a = [
        "Safety Exposure: Model has ingested the entire open internet; filtering guardrails are perpetually playing catch-up.",
        "Privacy Leaks: Student chats, homework errors, and voice inputs are sent to costly cloud servers.",
        "Always-Online Tether: Requires high-bandwidth internet, opening doors to digital distraction and online security risks."
    ]
    for b in bullets17_a:
        p = tf17_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf17_b = add_card(s17, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Cognitive & Curricular Pitfalls", SLATE_GRAY)
    bullets17_b = [
        "Sycophancy Loop: The student asserts broken logic and the LLM politely 'yes-ands' the child to remain agreeable.",
        "Context Vacuum: The LLM does not know Chapter 4; it approximates all math curricula it has ever seen.",
        "Right Answer, Wrong Method: Uses advanced shortcuts or high school algebra, failing the student on tomorrow's test.",
        "Mediocrity Collapse: Word problems collapse into generic, bland statistical averages."
    ]
    for b in bullets17_b:
        p = tf17_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s17, "When a 10-year-old studies with an ungrounded LLM, parents see an AI tutor, but engineers see open-world liabilities: sycophancy, privacy leaks, and wrong methods.")

    # SLIDE 18: CDE Alternative - Diagnostic Tutoring
    s18 = add_base_slide("Slide 17: The CDE Alternative — Deterministic Diagnostic Tutoring", "Isolating root-cause misconceptions via Discriminate and Correlate")
    tf18_a = add_card(s18, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "100% Offline & Grounded", PRIMARY_BLUE)
    bullets18_a = [
        "Local Execution: Runs completely offline on a low-cost student laptop or tablet (< 1 MiB binary).",
        "Strict Chapter Boundary: Bound strictly to the Chapter 4 instruction set—it physically cannot drift or teach unlearned shortcuts.",
        "Zero Privacy Risk: Student mistakes and session history never leave the device."
    ]
    for b in bullets18_a:
        p = tf18_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf18_b = add_card(s18, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Exact Root-Cause Diagnosis", SUCCESS_GREEN)
    bullets18_b = [
        "1. Discriminate (Pinpoint Divergence): Compares the student's erroneous step against the correct path to isolate the discriminant opcode (C_delta).",
        "2. Correlate (Find Common Root): Joins errors across 3 missed problems to reveal a single upstream gap (e.g., ADDITIVE_STERIC_ANALYSIS in Chapter 3).",
        "3. Targeted Remediation: Queries the local instruction set to generate tailored practice questions that test true mastery."
    ]
    for b in bullets18_b:
        p = tf18_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s18, "CDE provides deterministic diagnostic tutoring. When a student misses three questions, Discriminate pinpoints the exact broken step, and Correlate traces all three back to a single upstream root cause.")

    # SLIDE 19: Local Domain LLM & Gamification
    s19 = add_base_slide("Slide 18: The Bounded Interface — Clean-Room Local Models & Gamification", "Safety by construction and interactive learning loops")
    tf19_a = add_card(s19, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Clean-Room Local Model", PRIMARY_BLUE)
    bullets19_a = [
        "Specialized Training Boundary: A small local LLM trained exclusively on a 'Helpful Teacher' corpus and the textbook vocabulary.",
        "Safety by Construction: The model literally cannot hallucinate mature or toxic content because it has never ingested the open internet.",
        "Low Compute Footprint: Optimized for on-device inference, eliminating cloud GPU subscriptions."
    ]
    for b in bullets19_a:
        p = tf19_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf19_b = add_card(s19, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Interactive Gamification", ACCENT_TEAL)
    bullets19_b = [
        "Beyond the Boring Chatbox: Because logic is compiled into discrete opcodes, interfaces can render rich game mechanics:",
        "• Opcode Quest: Solve dungeon puzzles by selecting valid mathematical operations.",
        "• Bug Hunter: Find the broken step in an animated character's homework.",
        "• Themed Upscaling: Math problems dynamically skinned in Minecraft, space exploration, or athletics themes."
    ]
    for b in bullets19_b:
        p = tf19_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s19, "A small local model trained only on teacher dialogue and the textbook is safe by construction. Because logic is discrete, we can build educational games where the math is always certifiably sound.")

    # SLIDE 20: Local Memory Vault
    s20 = add_base_slide("Slide 19: The Local Memory Vault — Private, Deep Student Profiling", "Redefining 'Deep Knowledge' from the student's individualized perspective")
    tf20_a = add_card(s20, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Zero-Leakage Longitudinal Analytics", PRIMARY_BLUE)
    bullets20_a = [
        "100% Local Storage: Student history is stored in an encrypted on-device database—zero tracking, zero ad profiling.",
        "Opcode Mastery Heatmap: Tracks exactly which concepts the child knows by heart vs. which trigger repeated reasoning faults.",
        "Study Pace Correlation: Correlates daily study duration with test retention curves over days and weeks."
    ]
    for b in bullets20_a:
        p = tf20_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf20_b = add_card(s20, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Redefining Deep Knowledge", SUCCESS_GREEN)
    bullets20_b = [
        "Affective & Fatigue Signals: Monitors erratic input speed or hesitation to detect when the child is fatigued or overwhelmed.",
        "Open-World vs. True Depth: Open AI defines depth as encyclopedic trivia. CDE defines Deep Knowledge as:",
        "• Exhaustive mastery over the bounded domain.",
        "• Complete longitudinal understanding of the individual learner."
    ]
    for b in bullets20_b:
        p = tf20_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s20, "Because the system runs on bare metal, it can safely accumulate a deep memory profile: concept mastery, study time, and fatigue signals—without ever leaking student data.")

    # SLIDE 21: Personality as Interface & Nurse Module
    s21 = add_base_slide("Slide 20: Personality as Interface & Composable Domains", "Adaptive delivery, stacking curricula, and the School Nurse module")
    tf21_a = add_card(s21, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "Interchangeable Personas", PRIMARY_BLUE)
    bullets21_a = [
        "Decoupling Tone from Truth: In CDE, personality lives strictly in the interface. The math never bends.",
        "Adaptive Delivery Masks:",
        "• Bubbly & Supportive: Encouragement for high-anxiety sessions.",
        "• Quirky & Creative: Off-beat metaphors for creative thinkers.",
        "• Structured & Disciplined: Step-by-step clarity for analytical minds.",
        "• Rigorous & Demanding: Rapid-fire challenges for advanced students."
    ]
    for b in bullets21_a:
        p = tf21_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(8)

    tf21_b = add_card(s21, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "Domain Aggregation & Wellness", ACCENT_TEAL)
    bullets21_b = [
        "Stacking Domains: Grade 4 Math links to Grade 4 Science, sitting atop prior years as immutable prerequisites.",
        "The School Nurse & Wellness Module:",
        "• Nutrition, diet, and healthy habit education.",
        "• Ergonomics, sleep hygiene, and outdoor activity balance.",
        "• Safe Escalation Boundary: Refuses medical diagnosis. Directs the child to an adult: 'Let\'s ask mom, dad, or your doctor.'"
    ]
    for b in bullets21_b:
        p = tf21_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(8)

    set_speaker_note(s21, "Personality becomes an interchangeable skin. Domains stack cleanly: math connects to science, and alongside them sits a School Nurse module teaching nutrition and exercise with safe escalation boundaries.")

    # SLIDE 22: Regress Termination
    s22 = add_base_slide("Slide 21: Breaking the Epistemic Circle — Regress Termination", "How CDE structurally answers 'Who verifies the verifier?'")
    tf22_a = add_card(s22, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Dilemma Revisited", ALERT_RED)
    bullets22_a = [
        "The Open Loop: If Model A audits Model B, and Model B is audited by Model C, uncertainty is never removed.",
        "Continuous Uncertainty: Two neural models agreeing is merely shared probability, not verification.",
        "The Runaway Cost: Chaining models multiplies latency and cost without solving the fundamental vulnerability."
    ]
    for b in bullets22_a:
        p = tf22_a.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    tf22_b = add_card(s22, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), "The Structural Termination", SUCCESS_GREEN)
    bullets22_b = [
        "1. The Kernel Requires No Verification: It is a deterministic, inspectable finite-state machine. It adds zero uncertainty.",
        "2. Compilation Is Audited Offline: Validated by the domain authority against the stipulated answer key (X, Y).",
        "3. Ground Truth Is Stipulated: The regress terminates because ground truth is designated, bounded, and versioned.",
        "Verification terminates at the boundary of the stipulated artifact."
    ]
    for b in bullets22_b:
        p = tf22_b.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_BLACK
        p.space_before = Pt(10)

    set_speaker_note(s22, "We have answered the opening question. The infinite regress terminates because the kernel is deterministic integer logic, and ground truth is stipulated by a versioned artifact.")

    # SLIDE 23: The Executive Scorecard (Comparison Table)
    s23 = add_base_slide("Slide 22: The Executive Scorecard — Frontier LLMs vs. CDE", "A high-impact architectural comparison across key operational dimensions")

    rows = 8
    cols = 3
    table_shape = s23.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tbl = table_shape.table
    tbl.columns[0].width = Inches(2.733)
    tbl.columns[1].width = Inches(4.5)
    tbl.columns[2].width = Inches(4.5)

    headers = ["Dimension", "Frontier LLM Paradigm", "Compiled Domain Expertise (CDE)"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)

    data = [
        ("Substrate & Hardware", "Cloud GPUs / Continuous FP16-FP32", "Local Standard CPU / Integer-Only Bare Metal"),
        ("Artifact Footprint", "Gigabytes to Terabytes (>10^9 weights)", "Explicit Target: < 1.0 MiB Binary"),
        ("Runtime Latency", "Hundreds of milliseconds to seconds", "< 50 Microseconds per query"),
        ("Ground Truth & Logic", "Probabilistic token likelihood P(Y|X)", "Relational Proof Graph & Discrete Opcodes"),
        ("Failure Behavior", "Silent hallucinations & 'yes-anding'", "Loud syntax halt / Out-of-domain rejection"),
        ("Student Privacy", "Queries logged to cloud servers", "100% On-Device, Zero-leakage memory vault"),
        ("Curricular Scope", "Unversioned blend of open internet", "Strictly versioned, closed textbook snapshot")
    ]

    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, text in enumerate(row_data):
            cell = tbl.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 1 else RGBColor(241, 245, 249)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = "Arial"
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_BLACK
            if col_idx == 0:
                p.font.bold = True

    set_speaker_note(s23, "Here is the entire engineering comparison at a glance: gigabytes vs. megabytes, cloud GPUs vs. bare silicon, silent hallucination vs. loud syntax halts.")

    # SLIDE 24: Conclusion Slide
    s24 = prs.slides.add_slide(blank_layout)
    bg24 = s24.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg24.fill.solid()
    bg24.fill.fore_color.rgb = DARK_NAVY
    bg24.line.fill.background()

    tb24 = s24.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.0))
    tf24 = tb24.text_frame
    tf24.word_wrap = True
    p = tf24.paragraphs[0]
    p.text = "THE ERA OF COMPILED INTELLIGENCE"
    p.font.name = "Arial"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    bullets24 = [
        "Severing Acquisition from Execution: Use high-capacity neural models in the factory to compile; execute on deterministic bare metal at runtime.",
        "Bounded, Durable Competence: Moving away from ungrounded open-world extrapolation toward certifiable, auditable domain mastery.",
        "AI Does Not Replace Compilers: AI IS THE COMPILER."
    ]
    for b in bullets24:
        p = tf24.add_paragraph()
        p.text = "• " + b
        p.font.name = "Arial"
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(203, 213, 225)
        p.space_before = Pt(16)

    set_speaker_note(s24, "Thank you. Compiled Domain Expertise demonstrates that domain competence does not require continuous deep neural inference. Within a versioned domain, expertise can be compiled into an exact, auditable, permanent instruction set.")

    prs.save(filename)
    print(f"Presentation saved successfully as '{filename}' with {len(prs.slides)} slides.")

if __name__ == '__main__':
    build_presentation()
