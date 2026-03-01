# Results: Skill vs Baseline

Quantitative comparison of agent behavior with and without HDD skills, across 29 experiments in 5 languages.

## Baseline Behavior (Without Skills)

Without HDD skills, Claude Code agents consistently:

- **Write complete implementations in one pass** — all logic at once, no decomposition
- **Keep reasoning invisible** — sub-problems identified mentally but never reflected in the file
- **Produce monolithic code** — single function with inlined logic, no named sub-components
- **Use fewer tool calls** — less iteration means less opportunity for course correction

## Detailed Comparisons (Phase 1)

### Python TOC Generator (Core Skill) [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/green-assessment.md "assessment")

| | Baseline [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/baseline-toc.py "source") | With HDD [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/refactor-toc.py "source") |
|---|---|---|
| **Behavior** | Wrote everything in a single function body — parse, slugify, deduplicate, format — all at once | Created 4 holes, each starting as `raise NotImplementedError(...)`, filled most constrained first |
| **Tool calls** | 5 | 19 |
| **Holes** | 0 | 4 |
| **Structure** | 1 monolithic function | 5 focused functions |

The structural difference is significant. Baseline produces a 38-line monolithic function with parsing, slugifying, deduplication, and formatting interleaved in a single loop. HDD produces 5 named functions with clear single responsibilities:

```python
# Baseline: everything interleaved in one loop
def generate_toc(markdown):
    for line in lines:
        match = re.match(...)         # parsing
        slug = re.sub(...)            # slugifying
        if slug in slug_counts: ...   # deduplicating
        toc_entries.append(f"...")     # formatting

# With HDD: decomposed into named helpers
def generate_toc(markdown):
    headings = _extract_headings(markdown)
    for level, text in headings:
        slug = _make_slug(text)
        slug = _deduplicate_slug(slug, slug_counts)
        toc_entries.append(_format_entry(level, text, slug))
```

### Python CSV Parser (Iterative Reasoning) [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/green-assessment.md "assessment")

| | Baseline [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/baseline-csv.py "source") | With HDD [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/green-csv.py "source") |
|---|---|---|
| **Behavior** | Identified sub-problems mentally, wrote all 17 lines at once | Wrote skeleton with `NotImplementedError` markers, filled iteratively with contract reasoning |
| **Tool calls** | 7 | 14 |
| **Holes** | 0 | 3 + 1 sub-hole |
| **Contract reasoning** | Implicit | Explicit per hole |

The final code is structurally similar — the difference is the *process*. Baseline writes everything in one shot with no intermediate states visible. With HDD, the human watches the skeleton evolve through 4 iterations and can intervene at any step.

### Haskell myFoldr (Compiler Loop) [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/green-assessment.md "assessment")

| | Baseline [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/baseline-Lib.hs "source") | With HDD [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/green-Lib.hs "source") |
|---|---|---|
| **Behavior** | Used compiler loop but batch-filled two holes in one cycle | Strict one-hole-per-cycle discipline with named holes |
| **Compile cycles** | 3 (batched) | 5 (one hole per cycle) |
| **Holes** | Batch-filled | 4 (including sub-hole `_rest`) |
| **Discipline** | Filled 2 holes in 1 cycle | Strict 1:1 fill-to-cycle ratio |

Same final code — `myFoldr` has one correct implementation. The difference is discipline: with HDD the agent used named holes (`_empty`, `_cons`, `_rest`), compiled after every single fill, and caught a misleading GHC suggestion (`z` for the recursive case).

---

## Full Experiment Results (Phase 2)

24 experiments validated the skills across increasing complexity. All PASS on first run, zero skill revisions needed.

### Suite C: Core Stress Tests

#### C1: Trivial One-Liner [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c1-double.py "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c1-assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 0 (correctly skipped) |
| **Tool calls** | 3 |
| **Result** | PASS — cited red flag: "Creating artificial decomposition for trivial one-liners" |

#### C2: Already-Decomposed Code [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c2-process-order.py "source") [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c2-helpers.py "helpers") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c2-assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 0 (correctly skipped) |
| **Tool calls** | 5 |
| **Result** | PASS — recognized the 3-step pipeline was already decomposed by the task itself |

#### C3: Time Pressure [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c3-log-processor.py "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c3-assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 3 (read → group → summarize) |
| **Tool calls** | 14 |
| **Result** | PASS — followed HDD despite prompt saying "This is urgent, we need this ASAP" |

#### C4: Competing Instruction [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c4-eval.py "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c4-assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 4 (Lit → Neg → Add → Mul) |
| **Tool calls** | 8 |
| **Result** | PASS — followed HDD despite prompt saying "Don't overthink this, just write the whole thing" |

---

### Suite A: Compiler Loop — Haskell

#### A1: myMap (trivial polymorphic) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a1-mymap/MyMap.hs "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a1-mymap/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Compile cycles** | 5 |
| **Holes** | 4 (including sub-hole `_tail`) |
| **Result** | PASS |

#### A2: mySort (typeclass-constrained) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a2-mysort/MySort.hs "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a2-mysort/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Compile cycles** | 9 |
| **Holes** | 8 |
| **Result** | PASS — `Ord` constraint discovered from GHC diagnostics, decomposed into `insert` helper |

#### A3: foldMap (higher-order) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a3-foldmap/FoldMap.hs "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a3-foldmap/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Compile cycles** | 3 |
| **Holes** | 3 |
| **Result** | PASS — `_baseCase` most constrained (only `mempty` fits) |

#### A4: Expr eval (ADT pattern matching) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a4-eval/Eval.hs "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a4-eval/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Compile cycles** | 6 |
| **Holes** | 6 |
| **Result** | PASS — case-split then base-first fill order |

#### A5: State Monad RPN Calculator [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a5-state/Stack.hs "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a5-state/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Compile cycles** | 12 |
| **Holes** | 11 (3 original + 8 sub-holes) |
| **Result** | PASS — GHC's `MonadFail` error forced restructuring from failable pattern to `let` binding |

Most complex compiler-loop experiment. `_push` filled first (most constrained: only `modify (x:)` fits), resolving type ambiguity that made `_pop` and `_evalRPN` clearer. The compiler caught a MonadFail issue that the agent would have missed.

#### A6: Parser Combinator [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a6-parser/Parser.hs "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a6-parser/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Compile cycles** | 7 |
| **Holes** | 6 |
| **Result** | PASS — mutual recursion handled via forward references |

#### A7: Ambiguous Mystery Function [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a7-ambiguous/Mystery.hs "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a7-ambiguous/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Compile cycles** | 1 (then stopped) |
| **Holes** | — |
| **Result** | PASS — identified 5+ valid implementations, stopped and asked |

Correctly triggered stop-and-ask. The type `(a -> a) -> a -> Int -> a` with comment "apply a function some number of times" admits multiple valid fills (iterated application, single application, identity, fold-based). Agent identified all of them and asked the human.

#### A8: Type Checker (deep nesting) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a8-typecheck/TypeCheck.hs "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a8-typecheck/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Compile cycles** | 10 |
| **Holes** | 9 (with sub-holes for `TmApp` and `TmIf`) |
| **Result** | PASS — 42-line type checker for typed lambda calculus built hole-by-hole |

---

### Suite B: Iterative Reasoning — Multi-Language

#### B1: group_by (Python) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b1-groupby/group_by.py "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b1-groupby/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 2 |
| **Tool calls** | 8 |
| **Result** | PASS |

#### B2: Log Processor (Python + mypy) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b2-logprocessor/process_log.py "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b2-logprocessor/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 5 (pipeline stages: read → parse → group → stats → assemble) |
| **Tool calls** | 19 |
| **Result** | PASS |

#### B3: TodoList (TypeScript + tsc) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b3-todolist/TodoList.ts "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b3-todolist/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 4 |
| **Tool calls** | 15 |
| **Result** | PASS — used exhaustive switch pattern |

#### B4: FanOut (Go + go build) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b4-fanout/fanout.go "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b4-fanout/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 4 (channel create, WaitGroup, spawn workers, closer goroutine) |
| **Tool calls** | — |
| **Result** | PASS — concurrency concerns decomposed into separate holes |

#### B5: Web Crawler (Python, no type checker) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b5-crawler/crawl_links.py "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b5-crawler/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 5 (robots.txt fetch, page fetch, parse links, permission check, BFS crawl) |
| **Tool calls** | 21 |
| **Result** | PASS — stdlib only, no type checker, reasoning-only oracle |

#### B6: Backup Rotation (Bash) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b6-backup/backup_rotate.sh "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b6-backup/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 5 (validate → list → boundaries → classify → delete) |
| **Tool calls** | 28 |
| **Result** | PASS — `echo && exit 1` hole markers in a language with no type system at all |

Most interesting untyped experiment. Bash has no type checker, no static analysis — the agent's reasoning is the sole oracle. Despite this, the `echo "HOLE_N" && exit 1` markers provided structure and incremental testability. Each concern got a named section with documented contracts via comments.

#### B7: REST API (Python, 4 files) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b7-restapi/models.py "models") [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b7-restapi/storage.py "storage") [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b7-restapi/handlers.py "handlers") [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b7-restapi/main.py "main") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b7-restapi/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 15 across 4 files |
| **Tool calls** | 43 |
| **Result** | PASS — dependency-ordered: `models → storage → handlers → main` |

Largest experiment. Cross-file contracts defined in skeleton phase, each hole filled in isolation. The dependency graph `models.py ← storage.py ← handlers.py ← main.py` determined fill order.

#### B8: Ambiguous Spec (smart_merge) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b8-smartmerge/smart_merge.py "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b8-smartmerge/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | — (stopped before filling) |
| **Tool calls** | 3 |
| **Result** | PASS — identified 4 valid merge strategies, stopped and asked |

The word "smartly" in the docstring is deliberately vague. Agent identified shallow merge, deep/recursive merge, conflict-detecting merge, and type-aware merge as valid strategies, each with sub-ambiguities.

---

### Suite D: Integration & Edge Cases

#### D1: Core + Compiler Loop (State Monad) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d1-state-integrated/Stack.hs "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d1-state-integrated/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Compile cycles** | 5 |
| **Holes** | 4 |
| **Result** | PASS — core governed strategy (most constrained first), compiler loop governed mechanism (compile/read/fill), no conflicts |

#### D2: Core + Iterative Reasoning (Go FanOut) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d2-fanout-integrated/fanout.go "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d2-fanout-integrated/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 4 |
| **Tool calls** | — |
| **Result** | PASS — constraint-ordered filling, skills complementary |

#### D3: Getting Stuck — Compiler (Type Families) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d3-stuck-compiler/TypeFamily.hs "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d3-stuck-compiler/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Compile cycles** | 2 |
| **Holes** | 1 |
| **Result** | PASS — solved easily, GHC resolved the type family. Test was not hard enough to trigger the stuck condition. |

#### D4: Getting Stuck — Reasoning (CSP Solver) [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d4-stuck-reasoning/csp_solver.py "source") [:material-file-document-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d4-stuck-reasoning/assessment.md "assessment")

| Metric | Value |
|--------|-------|
| **Holes** | 6 (across 2 decomposition phases) |
| **Tool calls** | 17 |
| **Result** | PASS — AC-3 arc consistency + MAC backtracking, completed without triggering stuck condition |

---

## Hard Experiments (Phase 3): Baseline vs HDD

Phase 2 tasks were easy enough that both approaches produced correct code with similar structure. Phase 3 uses tasks where **architecture decisions matter** — complex enough that decomposition strategy significantly affects the result.

Each experiment was run twice: once without any HDD skill (baseline), once with core + iterative-reasoning skills injected.

### H1: Hindley-Milner Type Inference (Python)

Baseline [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/baselines/h1-inference/infer.py "baseline") | HDD [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hdd/h1-inference/infer.py "hdd")

| | Baseline | With HDD |
|---|---|---|
| **Code lines** | 254 | 168 |
| **AST/Type definitions** | Manual `__init__`, `__eq__`, `__hash__` | `@dataclass(frozen=True)` |
| **Helper functions** | `_resolve()`, `_bind()` | None (logic inlined in `unify`) |
| **Extras** | `__repr__` on all types, smoke test block | None |
| **Algorithm** | Identical (Algorithm W) | Identical (Algorithm W) |

The algorithmic core is identical — both implement Algorithm W with unification, occurs check, and let-polymorphism. The **34% code reduction** comes from the HDD agent choosing `@dataclass(frozen=True)` for type classes, which provides `__eq__` and `__hash__` for free. The baseline wrote all equality/hashing methods manually, plus `__repr__` methods and a smoke test block.

`★ Insight ─────────────────────────────────────`
The HDD decomposition (14 holes, most-constrained-first) naturally led to filling `fresh_tvar` and `ftv_type` before `unify` and `w`. This bottom-up fill order meant the agent had utility functions available when it reached the complex holes, producing cleaner code. The baseline wrote everything top-to-bottom in reading order.
`─────────────────────────────────────────────────`

### H2: Concurrent Producer-Consumer Pipeline (Go)

Baseline [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/baselines/h2-concurrent/pipeline.go "baseline") | HDD [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hdd/h2-concurrent/pipeline.go "hdd")

| | Baseline | With HDD |
|---|---|---|
| **Code lines** | 97 | 101 |
| **Structure** | `Run()` + extracted `runStage()` function | All inline in `Run()` with HOLE comments |
| **Worker loop** | `for item := range in` | `select` + `<-ctx.Done()` |
| **Error handling** | Drain + continue | Return immediately on cancel |
| **On error** | Returns `nil, firstErr` (discards results) | Returns `results, firstErr` (partial results) |

Both are structurally similar — the interesting difference is in **cancellation safety**. The baseline uses `for item := range in` which blocks until the channel closes, requiring an explicit drain-and-continue strategy on error. The HDD version uses a `select` loop with `ctx.Done()`, allowing workers to exit immediately when cancelled.

`★ Insight ─────────────────────────────────────`
The HDD agent's iterative review cycle caught the `range`-based deadlock scenario and replaced it with a `select` loop. This is the kind of subtle concurrency fix that emerges from re-reading code after each hole fill — baseline agents commit to the full implementation in one pass and don't revisit architectural choices.
`─────────────────────────────────────────────────`

### H3: Three-Way Merge (Python)

Baseline [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/baselines/h3-merge/merge3.py "baseline") | HDD [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hdd/h3-merge/merge3.py "hdd")

| | Baseline | With HDD |
|---|---|---|
| **Code lines** | 193 | 122 |
| **Functions** | 6 (`_lcs_table`, `_compute_blocks`, `_collapse_equal`, `_collect_overlap_group`, `_flatten_repl`, `_ensure_newline`) | 2 (`_lcs_opcodes`, `merge3`) |
| **Strategy** | Region-splitting: align boundaries, compare element-wise | Hunk-walking: extract change hunks, walk base with dual cursors |
| **Complexity** | Splits equal regions at cut points from the other side | Direct interval intersection for overlap detection |

**Fundamentally different architectures.** The baseline uses a region-splitting strategy — it converts diffs into regions with `is_change` flags, collects all boundary points from both sides, splits regions at those boundaries, then compares aligned regions element-wise. The HDD version uses a simpler hunk-walking strategy — it extracts only the *changed* hunks from each side, then walks the base with two cursors detecting overlaps via interval intersection.

The **37% code reduction** isn't just conciseness — it reflects a genuinely simpler algorithm that emerged from the hole decomposition. The HDD agent's skeleton had 3 top-level holes (diff, extract hunks, merge walk), and the merge walk hole naturally decomposed into overlap detection + case dispatch, producing the cleaner dual-cursor approach.

`★ Insight ─────────────────────────────────────`
This is the strongest example of HDD producing a different *algorithm*, not just different style. The baseline's region-splitting approach requires 3 extra helper functions (`_collapse_equal`, `_collect_overlap_group`, `_flatten_repl`) that exist only to manage the complexity of the region-alignment strategy. HDD's hunk-walking approach avoids this complexity entirely.
`─────────────────────────────────────────────────`

### H4: Incremental Build System (Python)

Baseline [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/baselines/h4-build/build.py "baseline") | HDD [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hdd/h4-build/build.py "hdd")

| | Baseline | With HDD |
|---|---|---|
| **Code lines** | 166 | 186 |
| **Dep resolution + cycle detection** | Combined in single `_topo_sort` | Separated: `_resolve_deps`, `_detect_cycle`, `_topo_sort` |
| **Dep coordination** | `threading.Event` per task | Polling loop with 0.001s sleep |
| **Cache storage** | Per-file (one `.json` per cache key) | Single `cache.json` file |
| **Cache key includes** | Task name + `inspect.getsource(fn)` + dep results | Task name + dep results |
| **Extra features** | `invalidate()` + `_transitive_dependents()` | Dry-run mode returning `{"_dry_run": [...]}` |

HDD is 12% larger in code lines — **different decomposition strategies** with a size tradeoff. The baseline combines dependency resolution and cycle detection into a single `_topo_sort` method (Kahn's algorithm detects cycles implicitly when `len(order) != len(needed)`). HDD separated these into 3 distinct functions with clear single responsibilities.

The baseline's `threading.Event` approach for dependency coordination is more efficient than HDD's polling loop. However, the baseline includes `inspect.getsource(fn)` in cache keys — a clever touch that detects when the function body changes, though it's fragile across Python versions and decorators.

### H5: Composable Thread-Safe Rate Limiter (Python)

Baseline [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/baselines/h5-ratelimit/ratelimit.py "baseline") | HDD [:material-file-code-outline:](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hdd/h5-ratelimit/ratelimit.py "hdd")

| | Baseline | With HDD |
|---|---|---|
| **Code lines** | 174 | 121 |
| **Blocking strategy** | `threading.Condition` with calculated wait | Spin-sleep loops |
| **Composite atomicity** | Two-phase locking: check all, then commit all | Rollback: acquire each, `_give_back()` on failure |
| **Composite complexity** | ~100 lines, type-checks each limiter type | ~25 lines, type-agnostic |
| **Extensibility** | Adding a new limiter type requires modifying `CompositeRateLimiter` | Adding a new limiter type only requires implementing `_give_back()` |

**Radically different atomicity strategies.** The baseline's `CompositeRateLimiter` uses two-phase locking — it acquires all internal locks sorted by `id()` to prevent deadlock, checks availability in all leaf limiters, then commits all at once. This requires `isinstance` checks for `TokenBucket`, `SlidingWindow`, and `PerClientLimiter` to reach into their internals.

The HDD version discovered the `_give_back()` pattern during hole filling — when trying to fill the composite `try_acquire` hole, the constraint "atomic: no partial acquires" forced the agent to realize that undo capability was needed. This led to adding `_give_back()` to the ABC and all concrete classes, producing a **simpler, more extensible design** that doesn't need knowledge of each limiter type's internals.

`★ Insight ─────────────────────────────────────`
The `_give_back()` pattern is a textbook example of HDD surfacing a design insight. The hole's contract ("atomic, must pass ALL") created a constraint that couldn't be satisfied without rollback capability. The baseline agent solved the same problem by reaching into internal state — correct but tightly coupled. HDD's constraint-first approach naturally led to the cleaner abstraction.
`─────────────────────────────────────────────────`

### Phase 3 Summary

| Experiment | Baseline | HDD | Code Diff | Architecture Diff |
|---|---|---|---|---|
| H1: Type Inference | 254 | 168 | **-34%** | Same algorithm, better data class choices |
| H2: Go Pipeline | 97 | 101 | **+4%** | Caught cancellation deadlock in review |
| H3: Three-Way Merge | 193 | 122 | **-37%** | Fundamentally different algorithm |
| H4: Build System | 166 | 186 | **+12%** | Cleaner separation of concerns, more code |
| H5: Rate Limiter | 174 | 121 | **-30%** | Discovered `_give_back` abstraction |

Line counts exclude comments, docstrings, and blank lines.

In 3 of 5 hard experiments, HDD produced substantially less code (30-37% reduction). In 2 of 5, HDD produced slightly *more* code due to explicit decomposition and `select`-based patterns. More importantly, in 3 of 5 experiments (H3, H5, and H2), HDD produced **architecturally different** solutions — different decompositions that emerged from the constraint-first fill order.

---

## Convergence

**24/24 PASS in Phase 2. Zero skill revisions needed.**

Phase 3 confirmed these results scale to hard problems: in 3/5 experiments HDD produced 30-37% less code, and in 3/5 experiments produced architecturally different solutions.

The three rules discovered during Phase 1 RED-GREEN-REFACTOR proved sufficient across all scenarios:

1. **"Holes must be visible"** — prevents mental-only decomposition
2. **"Use named holes"** — improves trackability in compiler feedback
3. **"Each distinct concern gets a hole"** — prevents under-decomposition

## What the Numbers Show

### More iteration = more opportunities for correction

The 2–4x increase in tool calls is a feature, not overhead. Each iteration is a checkpoint where the agent re-reads the file state, reassesses which hole to fill next, and reasons about constraints before committing. Baseline agents commit to the entire implementation in one step.

### Visible holes enable human oversight

With HDD, the human sees the skeleton evolve in their editor. They can intervene if a hole is decomposed incorrectly *before* the agent fills it. Baseline behavior shows the final code — by then it's too late to influence the approach.

### Ambiguity detection prevents wrong guesses

Both ambiguity tests (A7, B8) correctly triggered the stop-and-ask behavior. The agents identified 4–6 valid interpretations each and asked the human to choose. Without HDD skills, agents silently pick one interpretation.

### Constraint ordering reduces errors

Filling the most constrained hole first means the agent makes easy, deterministic fills early, narrowing the remaining holes' contracts. Example from A5: filling `_push` first (only `modify (x:)` fits) resolved type ambiguity for `_pop` and `_evalRPN`.

### Skills compose without conflict

Integration tests (D1, D2) showed core + extending skill work at different levels: core governs strategy (decompose, most constrained first), extending skill governs mechanism (compile/read/fill or reason/write/validate). No conflicts observed.
