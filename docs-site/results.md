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

=== "With HDD"

    Agent created 4 holes (`_extract_headings`, `_make_slug`, `_deduplicate_slug`, `_format_entry`), each starting as `raise NotImplementedError(...)`. Filled most constrained first (`_format_entry` → `_deduplicate_slug` → `_extract_headings` → `_make_slug`). 19 tool calls.

### Python CSV Parser (Iterative Reasoning)

=== "Baseline"

    Agent identified sub-problems (row splitting, quote-aware parsing, header mapping) in its reasoning, but wrote all 17 lines at once. The human never sees intermediate states. 7 tool calls.

=== "With HDD"

    Agent wrote skeleton with `NotImplementedError` hole markers. Filled HOLE_1 (parse_row) first because HOLE_2 depends on it. Explicit contract reasoning before each fill. 14 tool calls.

### Haskell myFoldr (Compiler Loop)

=== "Baseline"

    When instructed to use HDD, agent used the compiler loop but batch-filled two holes in one cycle.

=== "With HDD"

    Strict one-hole-per-cycle discipline. Named holes (`_empty`, `_cons`, `_rest`). 5 compile cycles. Caught misleading GHC suggestion (`z` for the recursive case) by cross-referencing with function purpose.

## Phase 2: Full Experiment Results

### All 24 Experiments

| # | Name | Skill | Lang | Holes | Cycles/Calls | Result |
|---|------|-------|------|-------|-------------|--------|
| C1 | Trivial one-liner | Core | — | 0 (skipped) | — | PASS — correctly skipped HDD |
| C2 | Already-decomposed | Core | — | 0 (skipped) | — | PASS — no artificial holes |
| C3 | Time pressure | Core | Py | 3 | 14 calls | PASS — resisted urgency |
| C4 | Competing instruction | Core | Py | 4 | 8 calls | PASS — overrode "just write it" |
| A1 | myMap | Compiler | Hs | 4 | 5 cycles | PASS |
| A2 | mySort | Compiler | Hs | 8 | 9 cycles | PASS — Ord from diagnostics |
| A3 | foldMap | Compiler | Hs | 3 | 3 cycles | PASS — mempty most constrained |
| A4 | Expr eval | Compiler | Hs | 6 | 6 cycles | PASS |
| A5 | State monad RPN | Compiler | Hs | 11 | 12 cycles | PASS — MonadFail caught |
| A6 | Parser combinator | Compiler | Hs | 6 | 7 cycles | PASS — mutual recursion |
| A7 | Ambiguous mystery | Compiler | Hs | — | 1 cycle | PASS — stopped, 5+ options |
| A8 | Type checker | Compiler | Hs | 9 | 10 cycles | PASS — sub-holes |
| B1 | group_by | Reasoning | Py | 2 | 8 calls | PASS |
| B2 | Log processor | Reasoning | Py | 5 | 19 calls | PASS — pipeline stages |
| B3 | TodoList | Reasoning | TS | 4 | 15 calls | PASS — exhaustive switch |
| B4 | FanOut | Reasoning | Go | 4 | — | PASS — concurrency decomposed |
| B5 | Web crawler | Reasoning | Py | 5 | 21 calls | PASS — no type checker |
| B6 | Backup rotation | Reasoning | Bash | 5 | 28 calls | PASS — echo+exit markers |
| B7 | REST API | Reasoning | Py | 15 | 43 calls | PASS — 4 files |
| B8 | Ambiguous merge | Reasoning | Py | — | 3 calls | PASS — stopped, 4 strategies |
| D1 | Core + compiler | Both | Hs | 4 | 5 cycles | PASS — skills complementary |
| D2 | Core + reasoning | Both | Go | 4 | — | PASS — constraint-ordered |
| D3 | Stuck (type family) | Compiler | Hs | 1 | 2 cycles | PASS — solved easily |
| D4 | Stuck (CSP solver) | Reasoning | Py | 6 | 17 calls | PASS — AC-3 + backtracking |

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
