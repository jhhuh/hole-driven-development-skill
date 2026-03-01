# Results: Skill vs Baseline

Quantitative comparison of agent behavior with and without HDD skills, across 24 experiments in 5 languages.

## Baseline Behavior (Without Skills)

Without HDD skills, Claude Code agents consistently:

- **Write complete implementations in one pass** — all logic at once, no decomposition
- **Keep reasoning invisible** — sub-problems identified mentally but never reflected in the file
- **Produce monolithic code** — single function with inlined logic, no named sub-components
- **Use fewer tool calls** — less iteration means less opportunity for course correction

This was observed across all three baseline tests (Python TOC generator, Haskell myFoldr, Python CSV parser).

## With HDD Skills

| Metric | Baseline | With HDD Skills | Change |
|--------|----------|-----------------|--------|
| Visible decomposition | Never | Always | Holes in the file at every step |
| Tool calls (Python TOC) | 5 | 19 | 3.8x more iteration |
| Tool calls (CSV parser) | 7 | 14–15 | 2x more iteration |
| Holes created | 0 | 2–15 per task | Explicit sub-problems |
| Code structure | Monolithic | Modular helpers | Named functions per concern |
| Contract reasoning | Implicit | Explicit per hole | Stated before each fill |
| Fill ordering | N/A (all at once) | Most constrained first | Reduces errors |
| Ambiguity detection | Never triggered | Correctly stopped (A7, B8) | Prevents wrong guesses |

## Detailed Comparisons

### Python TOC Generator (Core Skill)

=== "Baseline"

    Agent wrote everything in a single function body — parse, slugify, deduplicate, format — all at once. No decomposition visible in the file. 5 tool calls.

    [:material-file-code: baseline-toc.py](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/baseline-toc.py)

=== "With HDD"

    Agent created 4 holes (`_extract_headings`, `_make_slug`, `_deduplicate_slug`, `_format_entry`), each starting as `raise NotImplementedError(...)`. Filled most constrained first (`_format_entry` → `_deduplicate_slug` → `_extract_headings` → `_make_slug`). 19 tool calls.

    [:material-file-code: green-toc.py](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/green-toc.py) · [:material-file-document: assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/green-assessment.md)

### Python CSV Parser (Iterative Reasoning)

=== "Baseline"

    Agent identified sub-problems (row splitting, quote-aware parsing, header mapping) in its reasoning, but wrote all 17 lines at once. The human never sees intermediate states. 7 tool calls.

    [:material-file-code: baseline-csv.py](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/baseline-csv.py)

=== "With HDD"

    Agent wrote skeleton with `NotImplementedError` hole markers. Filled HOLE_1 (parse_row) first because HOLE_2 depends on it. Explicit contract reasoning before each fill. 14 tool calls.

    [:material-file-code: green-csv.py](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/green-csv.py) · [:material-file-document: assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/green-assessment.md)

### Haskell myFoldr (Compiler Loop)

=== "Baseline"

    When instructed to use HDD, agent used the compiler loop but batch-filled two holes in one cycle.

    [:material-file-code: baseline-Lib.hs](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/baseline-Lib.hs)

=== "With HDD"

    Strict one-hole-per-cycle discipline. Named holes (`_empty`, `_cons`, `_rest`). 5 compile cycles. Caught misleading GHC suggestion (`z` for the recursive case) by cross-referencing with function purpose.

    [:material-file-code: green-Lib.hs](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/green-Lib.hs) · [:material-file-document: assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/green-assessment.md)

## Phase 2: Full Experiment Results

### All 24 Experiments

| # | Name | Skill | Lang | Holes | Cycles/Calls | Result | Source |
|---|------|-------|------|-------|-------------|--------|--------|
| C1 | Trivial one-liner | Core | — | 0 (skipped) | — | PASS — correctly skipped HDD | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c1-double.py) |
| C2 | Already-decomposed | Core | — | 0 (skipped) | — | PASS — no artificial holes | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c2-process-order.py) |
| C3 | Time pressure | Core | Py | 3 | 14 calls | PASS — resisted urgency | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c3-log-processor.py) |
| C4 | Competing instruction | Core | Py | 4 | 8 calls | PASS — overrode "just write it" | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-core/results/c4-eval.py) |
| A1 | myMap | Compiler | Hs | 4 | 5 cycles | PASS | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a1-mymap/MyMap.hs) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a1-mymap/assessment.md) |
| A2 | mySort | Compiler | Hs | 8 | 9 cycles | PASS — Ord from diagnostics | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a2-mysort/MySort.hs) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a2-mysort/assessment.md) |
| A3 | foldMap | Compiler | Hs | 3 | 3 cycles | PASS — mempty most constrained | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a3-foldmap/FoldMap.hs) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a3-foldmap/assessment.md) |
| A4 | Expr eval | Compiler | Hs | 6 | 6 cycles | PASS | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a4-eval/Eval.hs) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a4-eval/assessment.md) |
| A5 | State monad RPN | Compiler | Hs | 11 | 12 cycles | PASS — MonadFail caught | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a5-state/Stack.hs) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a5-state/assessment.md) |
| A6 | Parser combinator | Compiler | Hs | 6 | 7 cycles | PASS — mutual recursion | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a6-parser/Parser.hs) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a6-parser/assessment.md) |
| A7 | Ambiguous mystery | Compiler | Hs | — | 1 cycle | PASS — stopped, 5+ options | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a7-ambiguous/Mystery.hs) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a7-ambiguous/assessment.md) |
| A8 | Type checker | Compiler | Hs | 9 | 10 cycles | PASS — sub-holes | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a8-typecheck/TypeCheck.hs) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development/results/a8-typecheck/assessment.md) |
| B1 | group_by | Reasoning | Py | 2 | 8 calls | PASS | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b1-groupby/group_by.py) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b1-groupby/assessment.md) |
| B2 | Log processor | Reasoning | Py | 5 | 19 calls | PASS — pipeline stages | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b2-logprocessor/process_log.py) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b2-logprocessor/assessment.md) |
| B3 | TodoList | Reasoning | TS | 4 | 15 calls | PASS — exhaustive switch | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b3-todolist/TodoList.ts) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b3-todolist/assessment.md) |
| B4 | FanOut | Reasoning | Go | 4 | — | PASS — concurrency decomposed | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b4-fanout/fanout.go) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b4-fanout/assessment.md) |
| B5 | Web crawler | Reasoning | Py | 5 | 21 calls | PASS — no type checker | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b5-crawler/crawl_links.py) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b5-crawler/assessment.md) |
| B6 | Backup rotation | Reasoning | Bash | 5 | 28 calls | PASS — echo+exit markers | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b6-backup/backup_rotate.sh) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b6-backup/assessment.md) |
| B7 | REST API | Reasoning | Py | 15 | 43 calls | PASS — 4 files | [code](https://github.com/jhhuh/hole-driven-development-skill/tree/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b7-restapi) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b7-restapi/assessment.md) |
| B8 | Ambiguous merge | Reasoning | Py | — | 3 calls | PASS — stopped, 4 strategies | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b8-smartmerge/smart_merge.py) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/hole-driven-development-iterative-reasoning/results/b8-smartmerge/assessment.md) |
| D1 | Core + compiler | Both | Hs | 4 | 5 cycles | PASS — skills complementary | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d1-state-integrated/Stack.hs) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d1-state-integrated/assessment.md) |
| D2 | Core + reasoning | Both | Go | 4 | — | PASS — constraint-ordered | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d2-fanout-integrated/fanout.go) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d2-fanout-integrated/assessment.md) |
| D3 | Stuck (type family) | Compiler | Hs | 1 | 2 cycles | PASS — solved easily | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d3-stuck-compiler/TypeFamily.hs) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d3-stuck-compiler/assessment.md) |
| D4 | Stuck (CSP solver) | Reasoning | Py | 6 | 17 calls | PASS — AC-3 + backtracking | [code](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d4-stuck-reasoning/csp_solver.py) · [assessment](https://github.com/jhhuh/hole-driven-development-skill/blob/@COMMIT_SHA@/tests/integration/results/d4-stuck-reasoning/assessment.md) |

### Convergence

**24/24 PASS. Zero skill revisions needed.**

## What the Numbers Show

### More iteration = more opportunities for correction

The 2–4x increase in tool calls is a feature, not overhead. Each iteration is a checkpoint where the agent:

- Re-reads the file state
- Reassesses which hole to fill next
- Reasons about constraints before committing

Baseline agents commit to the entire implementation in one step. If something is wrong, there's no intermediate state to roll back to.

### Visible holes enable human oversight

With HDD, the human sees the skeleton evolve in their editor. They can intervene if a hole is decomposed incorrectly *before* the agent fills it. Baseline behavior shows the final code — by then it's too late to influence the approach.

### Ambiguity detection prevents wrong guesses

Both ambiguity tests (A7: Haskell `mystery` function, B8: Python `smart_merge`) correctly triggered the stop-and-ask behavior. The agents identified 4–6 valid interpretations each and asked the human to choose.

Without HDD skills, agents silently pick one interpretation and implement it — the human may not realize a choice was made.

### Constraint ordering reduces errors

Filling the most constrained hole first (fewest valid implementations) means the agent makes easy, deterministic fills early. This narrows the remaining holes' contracts, making later fills easier too.

Example from A5 (State monad): filling `_push` first (only `modify (x:)` fits) resolved type ambiguity that made `_pop` and `_evalRPN` clearer to fill.

### Skills compose without conflict

Integration tests (D1, D2) showed core + extending skill work at different levels:

- **Core** governs strategy — decompose, fill most constrained first
- **Extending skill** governs mechanism — compile/read/fill (compiler) or reason/write/validate (reasoning)

No conflicts were observed. The skills address orthogonal concerns.

## Language-Specific Observations

### Haskell (compiler loop)

GHC's typed hole diagnostics provide *expected type*, *bindings in scope*, and *valid hole fits* — a rich oracle. Named holes (`_base`, `_recursive`) make diagnostics unambiguous. The compiler catches type errors immediately, so fills are verified at each cycle.

### Python, TypeScript, Go (iterative reasoning + type checker)

Optional type checkers (mypy, tsc, go build) validate fills but don't provide hole diagnostics. The agent reasons about contracts manually, then validates structurally. Still effective — B2 used 5 pipeline-stage holes with mypy validation.

### Bash (iterative reasoning, no type checker)

HDD works but with constraints:

- `echo "HOLE_N" && exit 1` markers kill the script, forcing sequential fill order
- No static verification of variable names (typo = silent empty variable)
- Contracts expressed as comments, not types
- Agent reasoning is the sole oracle

Despite this, B6 (backup rotation) produced well-structured code with 5 clearly bounded holes — better structure than typical bash scripts.

### Multi-file (iterative reasoning)

B7 (REST API) demonstrated HDD across 4 files with 15 holes. Dependency ordering:

```
models.py (2 holes) → storage.py (6 holes) → handlers.py (5 holes) → main.py (2 holes)
```

Cross-file contracts (imports, method signatures) were defined in the skeleton phase, so each hole could be filled in isolation.
