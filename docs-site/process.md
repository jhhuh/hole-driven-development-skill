# Development Process

How these skills were built and validated — using TDD applied to documentation.

## Methodology: RED-GREEN-REFACTOR for Skills

The same test-driven development cycle used for code was applied to skill creation. Each skill went through:

1. **RED** — Run a pressure scenario *without* the skill. Document baseline behavior.
2. **GREEN** — Write the skill. Re-run the same scenario. Verify behavior changes.
3. **REFACTOR** — Identify gaps, add rules, re-test until bulletproof.

This ensures every rule in the skill exists because an agent violated it during testing — not because it seemed like a good idea.

## Phase 1: Skill Creation

### Core Skill

**RED (baseline):** Agent given `generate_toc(markdown: str) -> str` — parse headings, build nested TOC with anchor links.

Result: Agent wrote the complete implementation in a single pass. All logic in one function body. No decomposition. 5 tool calls.

**GREEN (first draft):** Same scenario with core skill loaded.

Result: PARTIAL. Agent *did* decompose into 4 holes with correct constraint ordering — but kept the holes in its head. The file only showed the final code. Invisible decomposition defeats the purpose.

**REFACTOR:** Added two rules:

- "Holes must be visible — write holes to the file, not just in your reasoning"
- "One hole per iteration — fill exactly one hole, then reassess"

Re-test: PASS. Agent now writes `NotImplementedError` stubs, fills one per iteration. 19 tool calls. The human can watch the skeleton evolve.

### Compiler Loop Skill

**RED (baseline):** Agent given `myFoldr` type signature in Haskell.

Result: Baseline was tainted — prompt instructed agent to use HDD. But it revealed the agent *can* interact with GHC typed holes when told to, and that it batch-filled holes (filled 2 in one cycle).

**GREEN:** Same scenario with compiler loop skill loaded.

Result: PASS. 4 compile cycles, strict one-hole-per-cycle discipline. Agent used named holes (`_empty`, `_cons`) and caught a misleading fit where GHC suggested `z` for the recursive case.

**REFACTOR:** Added recommendation for named holes (`_name` instead of bare `_`).

### Iterative Reasoning Skill

**RED (baseline):** Agent given `parse_csv(text: str) -> list[dict[str, str]]`.

Result: Agent wrote 17-line complete implementation in one pass. 7 tool calls. It identified the same sub-problems that HDD would create as holes, but wrote them all at once.

**GREEN:** Same scenario with iterative reasoning skill loaded.

Result: PASS. 2 holes with `NotImplementedError` markers, filled iteratively with explicit contract reasoning. 14 tool calls.

**REFACTOR:** Added "each distinct concern gets a hole" — the GREEN test only created 2 holes for a 4-requirement spec.

### Key Rules Discovered

| Rule | Discovered during | Why it matters |
|------|-------------------|----------------|
| "Holes must be visible" | Core GREEN (PARTIAL) | Without it, agents decompose mentally but write complete code |
| "Use named holes" | Compiler-loop REFACTOR | Bare `_` makes diagnostics ambiguous across cycles |
| "Each concern gets a hole" | Iterative-reasoning REFACTOR | Prevents under-decomposition |

These three rules, discovered during Phase 1, proved sufficient for all 24 Phase 2 experiments without revision.

---

## Phase 2: Validation Experiments

24 experiments across 6 rounds, testing the skills against increasingly difficult scenarios.

### Experiment Design

| Suite | Experiments | What it tests |
|-------|-------------|---------------|
| **C: Core Stress** | C1–C4 | Edge cases, pressure resistance, competing instructions |
| **A: Compiler Loop** | A1–A8 | Trivial to complex Haskell (polymorphism → type checker) |
| **B: Iterative Reasoning** | B1–B8 | Multi-language (Python, TypeScript, Go, Bash), typed and untyped |
| **D: Integration** | D1–D4 | Skill composition, stuck/stop conditions |

### Round-by-Round Progression

**Round 1 — Core stress tests (C1–C4):**
Tested skill boundaries — trivial code that shouldn't be decomposed (C1), already-modular code (C2), time pressure (C3), and explicit "just write it" instruction (C4). All PASS.

**Round 2 — Compiler loop basics (A1–A4):**
Haskell implementations from trivial polymorphic (`myMap`) to ADT pattern matching (`Expr eval`). 3–9 compile cycles each. All PASS.

**Round 3 — Compiler loop advanced (A5–A8):**
State monad RPN calculator (12 cycles, 11 holes), parser combinators with mutual recursion, ambiguous specification (correctly stopped), deep nesting type checker (10 cycles, 9 holes). All PASS.

**Round 4 — Iterative reasoning with type checkers (B1–B4):**
Python with mypy, TypeScript with tsc, Go with go build. 2–5 holes each. All PASS.

**Round 5 — Iterative reasoning without type checkers (B5–B8):**
Python without mypy, Bash (no type system at all), multi-file REST API (15 holes across 4 files), ambiguous specification (correctly stopped). All PASS.

**Round 6 — Integration and edge cases (D1–D4):**
Core + compiler loop together, core + iterative reasoning together, "stuck" scenarios for both modes. All PASS.

### Convergence

**24/24 PASS on first run. Zero skill revisions triggered.**

The Skill Revision Log remained empty throughout Phase 2. The three rules discovered during Phase 1 RED-GREEN-REFACTOR were sufficient across all scenarios.

---

## Observations

### What worked well

- **TDD for skills catches issues early.** The three critical rules were all discovered during Phase 1 before any large-scale testing.
- **Visible holes are the key insight.** The single most impactful rule. Without it, agents appear to decompose but actually write monolithic code.
- **Named holes improve compiler feedback.** In Haskell, `_base` and `_recursive` produce clearer diagnostics than two bare `_` holes.
- **Concern-per-hole prevents under-decomposition.** Without this rule, agents collapse multiple sub-problems into one hole.

### What could be improved

- **D3/D4 "stuck" tests were too easy.** The type family problem was solved in 2 cycles; the CSP solver was completed without difficulty. Harder scenarios could stress-test the stop conditions.
- **Bash-specific ordering constraint.** The `echo && exit 1` hole marker kills the script, forcing holes to be filled in sequential order. In typed languages, holes can be filled in any order.

### Improvements made after Phase 2

- **Lean 4 and Rust support** added to the compiler loop skill (multi-language in one skill, not per-language extending skills).
- **VERIFY step** added after each fill — checks shared state, resource lifecycle, error paths. Triggered by Phase 3 blind review showing HDD lost 4/5 on bugs.
- **Monolithic algorithm guidance** — don't decompose tightly-coupled state machines. Triggered by H3 merge experiment where decomposition introduced seam bugs.
- **REVIEW-ALL holistic pass** added as final step before declaring done. Addresses systemic bugs that per-hole VERIFY can't catch.
