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

## 2026-03-01 — Phase 2: Experimentation complete, convergence achieved

### Summary
- 24 experiments across 6 rounds, all PASS on first run
- Zero skill revisions triggered during Phase 2
- Phase 1 RED-GREEN-REFACTOR caught all three critical rules upfront

### Round 1 — Core stress tests (C1-C4)
- C1: Trivial one-liner correctly skipped HDD (red flag works)
- C2: Already-decomposed code recognized — no artificial holes
- C3: Time pressure phrasing overridden — 3 holes, 14 tool calls
- C4: Competing "just write it" instruction overridden — 4 holes, 8 tool calls

### Round 2 — Compiler loop basics (A1-A4)
- A1 myMap: 5 cycles, 4 holes including sub-hole `_tail`
- A2 mySort: 9 cycles, 8 holes, `Ord` constraint discovered from GHC diagnostics
- A3 foldMap: 3 cycles, `_baseCase` most constrained (only `mempty` fits)
- A4 Expr eval: 6 cycles, case-split then base-first strategy

### Round 3 — Compiler loop advanced (A5-A8)
- A5 State monad: 12 cycles, 11 holes, MonadFail caught by compiler
- A6 Parser combinator: 7 cycles, mutual recursion via forward refs
- A7 Ambiguous mystery: Correctly stopped after 1 cycle, identified 5+ valid impls
- A8 Type checker: 10 cycles, 9 holes with sub-holes for TmApp/TmIf

### Round 4 — Iterative reasoning with type checkers (B1-B4)
- B1 Python group_by: 2 holes, 8 tool calls
- B2 Python log processor: 5 pipeline-stage holes, 19 tool calls
- B3 TypeScript TodoList: 4 holes, exhaustive switch pattern
- B4 Go FanOut: 4 concurrency-concern holes

### Round 5 — Iterative reasoning without type checkers (B5-B8)
- B5 Python crawler: 5 holes, BFS with robots.txt, stdlib only
- B6 Bash backup_rotate: 5 holes, echo+exit markers, 30 tool calls
- B7 Python multi-file REST API: 15 holes across 4 files, dependency-ordered
- B8 Ambiguous smart_merge: Correctly stopped, identified 4 strategies

### Round 6 — Integration & edge cases (D1-D4)
- D1 Core+compiler (State monad): 5 cycles, skills complementary, no conflicts
- D2 Core+reasoning (Go FanOut): 4 holes, constraint-ordered filling
- D3 Stuck-compiler (type families): Solved in 2 cycles — too easy, GHC resolved it
- D4 Stuck-reasoning (CSP solver): 6 holes, AC-3 + MAC backtracking, completed

### Convergence
All 24 experiments PASS on first run. The Skill Revision Log is empty — no revisions were needed. The three rules discovered during Phase 1 RED-GREEN-REFACTOR ("holes must be visible", "use named holes", "each concern gets a hole") were sufficient to guide correct behavior across all test scenarios.

### Observations for future work
- D3/D4 "stuck" tests were too easy — agents solved them. Harder stuck scenarios could stress-test the stop conditions more rigorously.
- Lean 4 and Rust support for the compiler-loop skill remains future work.
- The skills worked well across 5 languages (Haskell, Python, TypeScript, Go, Bash) without revision.
