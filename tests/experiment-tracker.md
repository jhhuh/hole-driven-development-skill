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
| D1 | Core + compiler loop (State monad) | 6 | 1 | | | |
| D2 | Core + reasoning (Go FanOut) | 6 | 1 | | | |
| D3 | Getting stuck — compiler (type families) | 6 | 1 | | | |
| D4 | Getting stuck — reasoning (CSP solver) | 6 | 1 | | | |

## Skill Revision Log

| Date | Skill | What changed | Triggered by |
|------|-------|-------------|-------------|
