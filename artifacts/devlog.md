# Devlog — Hole Driven Development Skills

## 2026-03-01 — Project kickoff

- Brainstormed design with user
- Three-layer architecture: core → compiler loop → iterative reasoning
- Core is ~150 words, stable
- Compiler loop starts Haskell-only, extensible to Lean 4 and Rust
- Iterative reasoning writes visible HOLE markers to file
- Full autonomy in the loop; stop on ambiguity or stuck
- Design doc committed

## 2026-03-01 — Phase 1: RED-GREEN-REFACTOR complete

### Core skill (hole-driven-development-core)
- RED: Baseline agent writes complete implementation in one pass (no decomposition)
- GREEN (PARTIAL): Agent decomposed into 4 holes with correct constraint ordering, BUT kept holes in its head — file only showed final code
- REFACTOR: Added "Holes must be visible" and "One hole per iteration" rules
- Re-test PASS: Agent now writes NotImplementedError stubs, fills one per iteration, 19 tool calls vs 5 in baseline

### Compiler-loop skill (hole-driven-development)
- RED: Baseline tainted (prompt told agent to use HDD). Agent CAN use compiler loop when instructed.
- GREEN (PASS): 4 compile cycles, named holes (_empty, _cons), strict one-per-cycle discipline
- REFACTOR: Added recommendation for named holes

### Iterative-reasoning skill (hole-driven-development-iterative-reasoning)
- RED: Agent writes complete CSV parser in one pass
- GREEN (PASS): 2 holes, filled iteratively with explicit contract reasoning, 14 tool calls vs 7
- REFACTOR: Added "each distinct concern gets a hole"

### Key learnings
1. "Holes must be visible" is critical — without it, agents decompose mentally but write complete code
2. Named holes improve trackability in compiler feedback
3. Each concern → at least one hole prevents under-decomposition
