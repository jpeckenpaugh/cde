# CDE Bounded Arithmetic Universe

## Purpose

This note uses elementary arithmetic to show how **Compiled Domain Expertise (CDE)** can be expressed as a small, closed, inspectable universe. It begins with addition and subtraction over a tiny input range, then extends the same design to multiplication and integer-only division.

The aim is not to replace mathematics. It is to demonstrate how a bounded domain can define exactly which inputs it accepts, which outputs it can produce, and which reasoning paths are licensed.

## CDE Background

**Compiled Domain Expertise (CDE)** separates the acquisition of knowledge from its execution. A capable model or human expert may be useful during development, but the deployed system executes an explicit, finite rule structure rather than relying on open-ended language generation.

**Empirical Knowledge Compilation (EKC)** is the build-time process of identifying useful concepts, testing their relationships to correct outcomes, and retaining the concepts and transitions that are supported by the domain. In a simple arithmetic domain, the rules are already known; EKC's role is easier to see as the process that would discover, test, and encode those rules.

The **Quantized Semantic Bottleneck Architecture (QSBA)** is the architectural boundary between flexible language at the outside and a discrete, typed core at the center. A user may phrase an arithmetic question in ordinary language, but the core should operate over a canonical representation such as `(7, +, 2)`.

The core artifact is a **Domain Instruction Set (DIS)**: a finite collection of typed concepts, terminal states, and licensed transitions. The DIS is not asked to improvise. It validates an input, activates the relevant concepts, and follows the permitted transition to an answer or an explicit boundary state.

In the examples below:

- `U` is the set of permitted input values.
- `X` is the set of valid canonical questions.
- `Y` is the set of terminal states, including numeric answers and any explicit boundary states.
- `C` is the set of concepts used to classify and validate a question before the DIS reaches a terminal state.

---

## Part I: A Smaller Bounded Universe

### 1. Input values

Start with the smallest useful universe:

```math
U = \{0,1,2,\dots,10\}
```

`U` is simply the set of values allowed as operands. A question in this universe may use 0 through 10, and no other input number.

### 2. Question set

Allow only addition and subtraction:

```math
X = \{(a,\mathrm{op},b) \mid a,b \in U,\ \mathrm{op}\in\{+,-\}\}
```

Each member of `X` is a structured question, not an ambiguous sentence. For example:

```math
(7,+,2), \quad (7,-,2), \quad (0,-,10)
```

There are 11 choices for the left operand, 2 operations, and 11 choices for the right operand:

```math
|X|=11\times2\times11=242
```

### 3. Terminal states

Addition can reach 20 and subtraction can reach -10, so the answer set is:

```math
Y = \{-10,-9,\dots,0,\dots,20\}
```

### 4. Concepts

The minimal concept set tracks the operand roles and operation:

```math
C =
\{\text{ADD},\text{SUBTRACT}\}
\cup
\{\text{LEFT-}n \mid n\in U\}
\cup
\{\text{RIGHT-}n \mid n\in U\}
```

For the question `(7, +, 2)`, the DIS activates:

```math
C(7,+,2)=\{\text{LEFT-7},\text{ADD},\text{RIGHT-2}\}
```

Those concepts license exactly this transition:

```math
7+2\rightarrow9
```

### 5. Example: evaluating `7 + 2 = 11`

The claim is:

```math
7+2=11
```

The number 11 is a valid member of `Y`; the system can represent it. But the active concepts for `(7, +, 2)` license 9, not 11:

```math
(7,+,2)\nrightarrow11
```

The DIS therefore rejects the claimed terminal state. This is an important distinction: it does **not** reject 11 as an impossible number. It rejects 11 because it is not connected to this input by a licensed arithmetic path.

---

## Part II: Extending the Universe

Now extend the operand range and add multiplication and division.

### 6. Expanded input values and question set

```math
U=\{0,1,2,\dots,20\}
```

```math
X=\{(a,\mathrm{op},b) \mid a,b\in U,\ \mathrm{op}\in\{+,-,\times,\div\}\}
```

There are 21 choices for each operand and 4 operations:

```math
|X|=21\times4\times21=1{,}764
```

### 7. Integer-only terminal states

The smallest numeric result is `0 - 20 = -20`; the largest is `20 x 20 = 400`:

```math
Y_{\text{integer}}=\{-20,-19,\dots,0,\dots,400\}
```

This universe permits integer outputs only. Fractions and remainders are not represented yet. To make that boundary explicit rather than silently guessing, add two typed terminal states:

```math
Y=Y_{\text{integer}}
\cup
\{\text{NON-WHOLE-RESULT},\text{UNDEFINED-DIVISION}\}
```

- `NON_WHOLE_RESULT` means that the arithmetic result is valid, but it is not an integer.
- `UNDEFINED_DIVISION` means the divisor is zero.

### 8. Extended concept set

The DIS now needs concepts for the new operators and guards for division:

```math
C=
\{\text{ADD},\text{SUBTRACT},\text{MULTIPLY},\text{DIVIDE}\}
\cup
\{\text{LEFT-}n,\text{RIGHT-}n \mid n\in U\}
\cup
\{\text{DIVISOR-NONZERO},\text{ZERO-DIVISOR},\text{DIVIDES-EVENLY},\text{NON-WHOLE-QUOTIENT}\}
```

The guard concepts are derived by validation. They determine which division transition is permitted.

### 9. Division transitions

For a nonzero divisor that divides evenly:

```math
(a,\div,b)\rightarrow a/b
\quad\text{when } b\neq0 \text{ and } b\mid a
```

For a nonzero divisor that does not divide evenly:

```math
(a,\div,b)\rightarrow\text{NON-WHOLE-RESULT}
\quad\text{when } b\neq0 \text{ and } b\nmid a
```

For division by zero:

```math
(a,\div,0)\rightarrow\text{UNDEFINED-DIVISION}
```

### 10. Example: evaluating `3 / 2`

Consider:

```math
x=(3,\div,2)
```

The system activates the input and operation concepts:

```math
\{\text{LEFT-3},\text{DIVIDE},\text{RIGHT-2}\}
```

It then validates the division:

```math
2\neq0
```

```math
2\nmid3
```

The result is not an integer, so the licensed transition is:

```math
(3,\div,2)\rightarrow\text{NON-WHOLE-RESULT}
```

This does not assert that division is impossible. Ordinary arithmetic gives:

```math
3\div2=1.5
```

Instead, the DIS reports that 1.5 is beyond the present output vocabulary. The arithmetic is valid; the result type is not yet supported by this bounded universe.

## Takeaway

The small and extended universes demonstrate the same CDE principle: a valid output is not merely a recognizable value. It must be the terminal state reached through a typed, explicitly licensed path from the given input.

That makes the boundary inspectable. `11` is representable but unlicensed for `7 + 2`; `1.5` is mathematically valid but intentionally outside the integer-only output domain for `3 / 2`. In both cases, the DIS responds with a deterministic and explainable result rather than inventing a justification.
