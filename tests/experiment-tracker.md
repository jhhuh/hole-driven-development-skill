# Experiment Tracker

## Status Legend
- **PASS**: Skill guides correct behavior
- **PARTIAL**: Some HDD behavior but with gaps
- **FAIL**: Skill fails to guide correct behavior
- **SKIP**: Experiment skipped (with reason)

## Suite C: Core Stress Tests

| # | Name | Round | Run | Grade | Revision | Notes |
|---|------|-------|-----|-------|----------|-------|
| C1 | Trivial one-liner | 1 | 1 | PASS | none | Correctly skipped HDD, cited red flag |
| C2 | Already-decomposed code | 1 | 1 | PASS | none | Recognized composition, no artificial holes |
| C3 | Time pressure phrasing | 1 | 1 | PASS | none | 3 holes, 14 tool calls despite urgency |
| C4 | Competing instruction | 1 | 1 | PASS | none | 4 holes, 8 tool calls, overrode "just write it" |

## Suite A: Compiler Loop — Haskell

| # | Name | Round | Run | Grade | Revision | Notes |
|---|------|-------|-----|-------|----------|-------|
| A1 | Trivial polymorphic (myMap) | 2 | 1 | PASS | none | 5 cycles, 4 holes, sub-hole _tail |
| A2 | Typeclass-constrained (mySort) | 2 | 1 | PASS | none | 9 cycles, 8 holes, Ord used from diagnostics |
| A3 | Higher-order multiple holes (foldMap) | 2 | 1 | PASS | none | 3 cycles, _baseCase most constrained |
| A4 | ADT pattern matching (Expr eval) | 2 | 1 | PASS | none | 6 cycles, case-split then base-first |
| A5 | Monadic code (State monad) | 3 | 1 | PASS | none | 12 cycles, 11 holes, MonadFail caught by compiler |
| A6 | Parser combinator | 3 | 1 | PASS | none | 7 cycles, 6 holes, mutual recursion via forward refs |
| A7 | Ambiguous hole (mystery) | 3 | 1 | PASS | none | Stopped after 1 cycle, identified 5+ valid impls |
| A8 | Deep nesting (type checker) | 3 | 1 | PASS | none | 10 cycles, 9 holes, sub-holes for TmApp/TmIf |

## Suite B: Iterative Reasoning — Multi-Language

| # | Name | Round | Run | Grade | Revision | Notes |
|---|------|-------|-----|-------|----------|-------|
| B1 | Python: group_by | 4 | 1 | PASS | none | 2 holes, 8 tool calls, visible markers |
| B2 | Python: log processor + mypy | 4 | 1 | PASS | none | 5 holes (pipeline stages), 19 tool calls |
| B3 | TypeScript: TodoList + tsc | 4 | 1 | PASS | none | 4 holes, 15 tool calls, exhaustive switch |
| B4 | Go: FanOut concurrency | 4 | 1 | PASS | none | 4 holes, concurrency concerns decomposed |
| B5 | Python: crawl_links (no type checker) | 5 | 1 | PASS | none | 5 holes, BFS with robots.txt, stdlib only |
| B6 | Bash: backup_rotate | 5 | 1 | PASS | none | 5 holes, echo+exit markers, 30 tool calls |
| B7 | Python: multi-file REST API | 5 | 1 | PASS | none | 15 holes across 4 files, dependency-ordered |
| B8 | Ambiguous spec (smart_merge) | 5 | 1 | PASS | none | Stopped, identified 4 strategies |

## Suite D: Integration & Edge Cases

| # | Name | Round | Run | Grade | Revision | Notes |
|---|------|-------|-----|-------|----------|-------|
| D1 | Core + compiler loop (State monad) | 6 | 1 | PASS | none | 5 cycles, skills complementary, no conflicts |
| D2 | Core + reasoning (Go FanOut) | 6 | 1 | PASS | none | 4 holes, constraint-ordered filling |
| D3 | Getting stuck — compiler (type families) | 6 | 1 | PASS | none | Solved in 2 cycles, GHC resolved type family |
| D4 | Getting stuck — reasoning (CSP solver) | 6 | 1 | PASS | none | 6 holes, AC-3 + MAC backtracking, completed |

## Suite H: Hard Experiments (Phase 3) — Blind Code Review

| # | Name | Round | Run | Baseline | HDD v2 | Winner | Notes |
|---|------|-------|-----|----------|--------|--------|-------|
| H1 | Hindley-Milner Type Inference | 7 | 2 | Bug 3 Arch 3 Prag 3 | Bug 4 Arch 4 Prag 5 | HDD v2 | VERIFY caught non-recursive subst chain |
| H2 | Concurrent Go Pipeline | 7 | 2 | Bug 3 Arch 4 Prag 4 | Bug 4 Arch 3 Prag 3 | HDD v2 | VERIFY caught data race on ch variable |
| H3 | Three-Way Merge | 7 | 3 | Bug 3 Arch 3 Prag 3 | Bug 4 Arch 5 Prag 5 | HDD v2 | Re-run with monolithic guidance; kept merge walk as single hole |
| H4 | Incremental Build System | 7 | 2 | Bug 4 Arch 3 Prag 4 | Bug 3 Arch 4 Prag 4 | HDD v2 | VERIFY caught invalidate_downstream bug |
| H5 | Composable Rate Limiter | 7 | 2 | Bug 2 Arch 2 Prag 2 | Bug 3 Arch 4 Prag 4 | HDD v2 | VERIFY caught two-phase atomicity issue |

## Convergence Status

**Phase 2: CONVERGED** — 24/24 PASS on first run, zero skill revisions.

**Phase 3: HDD v2 wins 5/5 blind reviews** after three skill improvements (VERIFY, monolithic guidance, REVIEW-ALL).

Five rules governing HDD:
1. **"Holes must be visible"** — prevents mental-only decomposition
2. **"Use named holes"** — improves trackability in compiler feedback
3. **"Each distinct concern gets a hole"** — prevents under-decomposition
4. **"Verify after filling"** — catches cross-hole interaction bugs
5. **"Don't decompose monolithic algorithms"** — tightly-coupled state machines stay as one hole

## Skill Revision Log

| Date | Skill | What changed | Triggered by |
|------|-------|-------------|-------------|
| 2026-03-01 | all three | Added VERIFY step after each fill | Phase 3 blind review: HDD lost 4/5 on bugs |
| 2026-03-01 | all three | Added "When NOT to decompose" monolithic guidance | H3 merge: decomposing dual-cursor walk introduced seam bugs |
| 2026-03-01 | all three | Added REVIEW-ALL holistic pass before done | Bug Hunter critique: systemic bugs hide in composition |
| 2026-03-01 | compiler-loop | Added Lean 4 support (sorry/_, lake build) | Language expansion |
| 2026-03-01 | compiler-loop | Added Rust support (todo!(), cargo build) | Language expansion |
