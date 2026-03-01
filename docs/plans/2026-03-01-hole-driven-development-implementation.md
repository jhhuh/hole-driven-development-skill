# Hole Driven Development Skills — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create three Claude Code skills enabling Hole Driven Development — a core philosophy skill and two extending skills (compiler loop, iterative reasoning).

**Architecture:** Three-layer skill hierarchy. Core defines the HDD loop abstractly. Compiler-loop skill drives real typed-hole compilers. Iterative-reasoning skill has Claude act as the type checker with visible hole markers. Each skill follows RED-GREEN-REFACTOR per writing-skills discipline.

**Tech Stack:** Claude Code skills (Markdown), Nix flake for dev environment, git

**Ref:** Design doc at `docs/plans/2026-03-01-hole-driven-development-design.md`

---

### Task 1: Project infrastructure

**Files:**
- Create: `flake.nix`
- Create: `CLAUDE.md`
- Create: `artifacts/devlog.md`
- Create: `.gitignore`

**Step 1: Create flake.nix**

Minimal Nix flake with devShell. Only needs `overmind`, `tmux`, and `ghc`/`cabal-install` (for testing the Haskell skill later).

```nix
{
  description = "Hole Driven Development skills for Claude Code";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          buildInputs = with pkgs; [
            overmind
            tmux
            ghc
            cabal-install
          ];
        };
      });
    };
}
```

**Step 2: Create CLAUDE.md**

```markdown
# Hole Driven Development Skills

## Project Structure

Three-layer skill hierarchy:
- `skills/hole-driven-development-core/` — HDD philosophy and abstract loop
- `skills/hole-driven-development/` — Compiler-feedback loop (Haskell first)
- `skills/hole-driven-development-iterative-reasoning/` — Claude-as-type-checker

## Dev Environment

`nix develop` provides ghc and cabal for testing the compiler-loop skill.

## Conventions

- Skills follow the writing-skills TDD discipline: RED → GREEN → REFACTOR
- Skill files are in `skills/<name>/SKILL.md`
- Test scenarios for skills go in `tests/<skill-name>/`
```

**Step 3: Create devlog and gitignore**

`artifacts/devlog.md`:
```markdown
# Devlog — Hole Driven Development Skills

## 2026-03-01 — Project kickoff

- Brainstormed design with user
- Three-layer architecture: core → compiler loop → iterative reasoning
- Core is ~150 words, stable
- Compiler loop starts Haskell-only, extensible to Lean 4 and Rust
- Iterative reasoning writes visible HOLE markers to file
- Full autonomy in the loop; stop on ambiguity or stuck
- Design doc committed
```

`.gitignore`:
```
result
.direnv
```

**Step 4: Commit**

```bash
git add flake.nix CLAUDE.md artifacts/devlog.md .gitignore
git commit -m "Add project infrastructure: flake, CLAUDE.md, devlog"
```

---

### Task 2: RED — Baseline test for core skill

**Files:**
- Create: `tests/hole-driven-development-core/scenario-1-decomposition.md`

**Step 1: Write pressure scenario**

This scenario tests whether an agent naturally decomposes top-down with holes vs. writing a complete implementation. The scenario should be a request to implement a moderately complex function where decomposition matters.

```markdown
# Scenario: Implement a markdown table-of-contents generator

## Setup
You are working on a utility that parses markdown and generates a table of contents.

## Prompt
Implement a function `generate_toc(markdown: str) -> str` that:
- Parses heading lines (# through ####)
- Generates a nested, indented TOC with links
- Handles duplicate headings by appending -1, -2, etc.
- Returns the TOC as a markdown string

## Expected WITHOUT skill (baseline)
Agent writes the complete implementation in one pass without decomposing into holes.

## Expected WITH skill
Agent decomposes: skeleton first, identifies sub-problems (parsing headings, slugifying, deduplication, indentation) as holes, fills them one at a time.
```

**Step 2: Run baseline with subagent**

Launch a subagent (general-purpose, no skill loaded) with the scenario prompt. Save output to `tests/hole-driven-development-core/baseline-1.md`.

Observe: Does the agent decompose top-down with holes, or write everything at once? Document rationalizations verbatim.

**Step 3: Commit**

```bash
git add tests/hole-driven-development-core/
git commit -m "Add baseline test scenario for core skill"
```

---

### Task 3: GREEN — Write `hole-driven-development-core` skill

**Files:**
- Create: `skills/hole-driven-development-core/SKILL.md`

**Step 1: Write the core skill**

Address the specific failures observed in the baseline. The skill should be ~150 words, defining:
- HDD philosophy (top-down decomposition with holes)
- The abstract loop (intention → skeleton → pick hole → determine needs → fill → repeat)
- Hole-filling strategy (most constrained first)
- Success criterion (no holes remain)
- What it does NOT cover (how to determine what a hole needs)

Frontmatter:
```yaml
---
name: hole-driven-development-core
description: Use when implementing functions or modules top-down by decomposing into typed holes, filling iteratively from most constrained to least
---
```

**Step 2: Run scenario WITH skill loaded**

Launch subagent with the same scenario, this time with the skill loaded. Verify agent now decomposes top-down with holes.

**Step 3: Commit**

```bash
git add skills/hole-driven-development-core/
git commit -m "Add hole-driven-development-core skill"
```

---

### Task 4: REFACTOR — Close loopholes in core skill

**Step 1: Analyze GREEN test output**

Compare baseline vs. with-skill behavior. Identify any new rationalizations or partial compliance (e.g., agent decomposes but fills all holes in one pass instead of iteratively).

**Step 2: Update skill to close loopholes**

Add explicit counters for observed rationalizations. Add red flags list if needed.

**Step 3: Re-test and commit**

```bash
git add skills/hole-driven-development-core/
git commit -m "Refactor core skill: close loopholes from testing"
```

---

### Task 5: RED — Baseline test for compiler-loop skill

**Files:**
- Create: `tests/hole-driven-development/scenario-1-haskell-holes.md`
- Create: `tests/hole-driven-development/test-project/` (minimal Haskell project)

**Step 1: Create a minimal Haskell test project**

A small Haskell file with a type signature and no implementation — the kind of thing HDD should handle.

```haskell
-- tests/hole-driven-development/test-project/Lib.hs
module Lib where

-- | Fold a list from the right
myFoldr :: (a -> b -> b) -> b -> [a] -> b
myFoldr = _
```

**Step 2: Write pressure scenario**

```markdown
# Scenario: Implement myFoldr using typed holes

## Setup
There is a Haskell file at tests/hole-driven-development/test-project/Lib.hs
with a type signature for myFoldr and a single typed hole.

## Prompt
Use hole-driven development to implement myFoldr. Run GHC to get
hole diagnostics and iteratively fill holes until the code compiles.

## Expected WITHOUT skill (baseline)
Agent writes the complete implementation directly without running GHC
or using typed hole feedback.

## Expected WITH skill
Agent runs GHC, reads hole diagnostics, fills one hole at a time
(possibly introducing new holes), repeats until compilation succeeds.
```

**Step 3: Run baseline, save output**

**Step 4: Commit**

```bash
git add tests/hole-driven-development/
git commit -m "Add baseline test for compiler-loop skill"
```

---

### Task 6: GREEN — Write `hole-driven-development` skill

**Files:**
- Create: `skills/hole-driven-development/SKILL.md`

**Step 1: Write the compiler-loop skill**

~200 words. Must reference core skill. Contents:
- REQUIRED BACKGROUND: `hole-driven-development-core`
- When to use (languages with typed holes, compiler available)
- The compiler-feedback loop (write holes → compile → parse diagnostics → fill → repeat)
- Autonomy rules (full autonomy, stop conditions)
- Compiler invocation table (Haskell only initially)
- Language detection logic

Frontmatter:
```yaml
---
name: hole-driven-development
description: Use when implementing in a language with typed holes (Haskell, Lean 4, Rust) where a compiler provides hole diagnostics — runs the compiler loop autonomously
---
```

**Step 2: Run scenario WITH skill, verify compliance**

**Step 3: Commit**

```bash
git add skills/hole-driven-development/
git commit -m "Add hole-driven-development compiler-loop skill"
```

---

### Task 7: REFACTOR — Close loopholes in compiler-loop skill

Same pattern as Task 4. Analyze, update, re-test, commit.

---

### Task 8: RED — Baseline test for iterative-reasoning skill

**Files:**
- Create: `tests/hole-driven-development-iterative-reasoning/scenario-1-python-holes.md`

**Step 1: Write pressure scenario**

```markdown
# Scenario: Implement a CSV parser with iterative reasoning

## Setup
Working in Python, no type checker configured.

## Prompt
Implement a function `parse_csv(text: str) -> list[dict[str, str]]` that:
- Splits into rows by newline
- Uses first row as headers
- Returns list of dicts mapping header to value
- Handles quoted fields with commas inside

## Expected WITHOUT skill (baseline)
Agent writes complete implementation without visible holes or
iterative decomposition.

## Expected WITH skill
Agent writes skeleton with HOLE markers visible in the file
(e.g., raise NotImplementedError("HOLE_1: ...")), then fills
them one at a time, reasoning about each hole's contract.
```

**Step 2: Run baseline, save output**

**Step 3: Commit**

```bash
git add tests/hole-driven-development-iterative-reasoning/
git commit -m "Add baseline test for iterative-reasoning skill"
```

---

### Task 9: GREEN — Write `hole-driven-development-iterative-reasoning` skill

**Files:**
- Create: `skills/hole-driven-development-iterative-reasoning/SKILL.md`

**Step 1: Write the iterative-reasoning skill**

~250 words. Must reference core skill. Contents:
- REQUIRED BACKGROUND: `hole-driven-development-core`
- When to use (any language, especially without typed holes)
- Hole marker format (language-appropriate `HOLE_N` placeholders written to file)
- The reasoning loop (skeleton → pick hole → reason about needs → fill → optionally validate → repeat)
- External tooling table (mypy, tsc, go build)
- Fallback (Claude's reasoning as sole oracle)
- Autonomy rules

Frontmatter:
```yaml
---
name: hole-driven-development-iterative-reasoning
description: Use when implementing in any language using top-down decomposition with visible hole markers, where Claude reasons about each hole's contract and fills iteratively
---
```

**Step 2: Run scenario WITH skill, verify compliance**

**Step 3: Commit**

```bash
git add skills/hole-driven-development-iterative-reasoning/
git commit -m "Add hole-driven-development-iterative-reasoning skill"
```

---

### Task 10: REFACTOR — Close loopholes in iterative-reasoning skill

Same pattern as Task 4. Analyze, update, re-test, commit.

---

### Task 11: Final integration check

**Step 1: Run all three scenarios with all skills loaded**

Verify the skills work together (core loaded as background, specific skill active).

**Step 2: Update devlog**

Append results and any learnings to `artifacts/devlog.md`.

**Step 3: Final commit**

```bash
git add -A
git commit -m "Complete initial skill suite: core, compiler-loop, iterative-reasoning"
```

---

## Phase 2: Iterative Experimentation and Optimization

Phase 1 produces working skills. Phase 2 proves they work, and **iteratively improves them** until they're robust. This phase is a loop, not a checklist.

### The Optimization Loop

```
┌─────────────────────────────────────────────────────────┐
│  1. SELECT batch of experiments (start with Suite A+C)  │
│  2. RUN each experiment with subagent                   │
│  3. GRADE: PASS / PARTIAL / FAIL                        │
│  4. ANALYZE failures — group by root cause              │
│  5. REVISE skill(s) to address root causes              │
│  6. RE-RUN failed experiments to verify fix             │
│  7. If new failure modes discovered → DESIGN new        │
│     experiments, add to tracker                         │
│  8. LOOP until current batch is all PASS                │
│  9. SELECT next batch → go to 2                         │
│                                                         │
│  EXIT when: all experiments PASS across 2 consecutive   │
│  full runs with no skill changes between them           │
└─────────────────────────────────────────────────────────┘
```

### Batch Strategy

Run experiments in progressive batches, not all 24 at once. Each batch targets one skill layer so revisions are focused:

| Round | Batch | Skills under test | Why this order |
|-------|-------|-------------------|----------------|
| 1 | C1–C4 (Core stress) | core | Validate foundation first |
| 2 | A1–A4 (Compiler easy) | core + compiler | Simple Haskell, verify basics |
| 3 | A5–A8 (Compiler hard) | core + compiler | Push compiler loop to limits |
| 4 | B1–B4 (Reasoning typed) | core + reasoning | Languages with type checkers |
| 5 | B5–B8 (Reasoning untyped) | core + reasoning | No type checker, edge cases |
| 6 | D1–D4 (Integration) | all | Layered architecture, stuck conditions |

Each round loops internally (run → grade → revise → re-run) until all experiments in the batch PASS.

### Evidence Format

Each experiment produces:

```
tests/<skill>/results/experiment-<id>-<name>/
├── run-1.md          # First attempt transcript
├── run-2.md          # After skill revision (if needed)
├── ...
└── assessment.md     # Final grade + root cause analysis
```

`assessment.md` format:
```markdown
# Experiment <id>: <name>

## Grade: PASS | PARTIAL | FAIL

## Behavior observed
[What the agent actually did — verbatim quotes of key moments]

## Root cause (if PARTIAL/FAIL)
[Why the skill failed to guide correct behavior]

## Skill revision triggered
[What was changed in SKILL.md, or "none"]

## Rationalizations observed
[Any excuses the agent made for skipping HDD — add to rationalization table]
```

### Convergence Criteria

The loop exits when:
1. All 24+ experiments grade PASS
2. A full re-run of all experiments (no cherry-picking) confirms PASS
3. No skill changes were needed between the two full runs

If convergence stalls (same experiment fails 3+ rounds), escalate:
- Re-examine the skill architecture (is the three-layer split right?)
- Consider if the experiment's success criteria are realistic
- Discuss with user before continuing

### Tracking

Maintain `tests/experiment-tracker.md`:

```markdown
| # | Batch | Name | Round | Run | Grade | Revision | Notes |
|---|-------|------|-------|-----|-------|----------|-------|
| C1 | 1 | Trivial one-liner | 1 | 1 | | | |
| C1 | 1 | Trivial one-liner | 1 | 2 | | | After revision |
```

The `Round` and `Run` columns track iteration history. A single experiment may have multiple rows as the skill is revised.

---

### Experiment Suite A: Compiler Loop — Haskell Typed Holes

These experiments progress from trivial to genuinely challenging, testing that the skill drives real compiler interaction at every difficulty level.

---

### Task 12: Experiment A1 — Trivial polymorphic function

**Scenario:**
```haskell
myMap :: (a -> b) -> [a] -> [b]
myMap = _
```

**Why this tests the skill:** Extremely constrained — almost one valid implementation. Tests that the agent still uses the compiler loop rather than just writing the answer (temptation to skip HDD is highest for easy problems).

**Success criteria:** Agent runs GHC, reads hole diagnostics, fills iteratively (even if it takes only 2 iterations). Does NOT just write the implementation directly.

---

### Task 13: Experiment A2 — Typeclass-constrained function

**Scenario:**
```haskell
mySort :: Ord a => [a] -> [a]
mySort = _
```

**Why this tests the skill:** The `Ord` constraint appears in hole diagnostics. Tests that the agent reads and uses typeclass information from GHC output to guide the implementation (e.g., recognizing it can use `compare`, `<=`).

**Success criteria:** Agent uses the `Ord` constraint info from hole diagnostics to select appropriate comparison operations. Doesn't just write a sort from memory.

---

### Task 14: Experiment A3 — Higher-order with multiple holes

**Scenario:**
```haskell
myFoldMap :: Monoid m => (a -> m) -> [a] -> m
myFoldMap f []     = _
myFoldMap f (x:xs) = _
```

**Why this tests the skill:** Two holes with different constraints. The empty case needs `mempty`, the cons case needs `mappend`/`<>`. Tests that the agent handles multiple holes and picks the most constrained first.

**Success criteria:** Agent fills the `[]` case first (more constrained — only `mempty` fits), then the `(x:xs)` case. Uses `Monoid` constraint from diagnostics.

---

### Task 15: Experiment A4 — Algebraic data type with pattern matching

**Scenario:**
```haskell
data Expr
  = Lit Int
  | Add Expr Expr
  | Mul Expr Expr
  | Neg Expr

eval :: Expr -> Int
eval = _
```

**Why this tests the skill:** Requires case splitting on a data type. Tests whether the agent introduces pattern match cases as sub-holes and fills them individually, rather than writing the whole evaluator at once.

**Success criteria:** Agent first introduces pattern matching on `Expr` constructors (each case as a hole), then fills each case. At least 4-5 compiler iterations.

---

### Task 16: Experiment A5 — Monadic code (State monad)

**Scenario:**
```haskell
import Control.Monad.State

type Stack = [Int]

push :: Int -> State Stack ()
push x = _

pop :: State Stack Int
pop = _

evalRPN :: [String] -> State Stack ()
evalRPN = _
```

**Why this tests the skill:** Multiple related functions, monadic context. Tests that the agent handles State monad types in hole diagnostics and fills functions in a sensible order (simpler ones first, then the one that depends on them).

**Success criteria:** Agent fills `push` and `pop` first (simpler, more constrained), then `evalRPN` which uses them. Correctly reads `State Stack` type from diagnostics.

---

### Task 17: Experiment A6 — Parser combinator (real-world complexity)

**Scenario:**
```haskell
-- Simple recursive descent parser for arithmetic expressions
-- expr   = term (('+' | '-') term)*
-- term   = factor (('*' | '/') factor)*
-- factor = '(' expr ')' | number

data Expr = Num Int | BinOp Char Expr Expr

parseExpr :: String -> Maybe (Expr, String)
parseExpr = _

parseTerm :: String -> Maybe (Expr, String)
parseTerm = _

parseFactor :: String -> Maybe (Expr, String)
parseFactor = _
```

**Why this tests the skill:** Mutually recursive functions, complex return types. This is a real-world Haskell pattern. Tests whether the skill handles inter-dependent holes and gradually builds up the implementation.

**Success criteria:** Agent works through the parser hierarchy, using compiler feedback at each step. Handles the mutual recursion without getting stuck.

---

### Task 18: Experiment A7 — Ambiguous hole (multiple valid implementations)

**Scenario:**
```haskell
mystery :: (a -> a) -> a -> Int -> a
mystery = _
```

**Why this tests the skill:** Multiple valid implementations (apply function N times? Ignore the Int? Apply once?). Tests the stop condition — agent should surface the ambiguity rather than picking arbitrarily.

**Success criteria:** Agent recognizes the ambiguity (GHC will show multiple valid hole fits) and STOPS to ask the human, rather than silently choosing one.

---

### Task 19: Experiment A8 — Large function with deep hole nesting

**Scenario:**
```haskell
-- Implement a simple type checker for a small language
data Type = TInt | TBool | TFun Type Type deriving (Eq, Show)
data Term = TmLit Int | TmBool Bool | TmVar String
           | TmApp Term Term | TmAbs String Type Term
           | TmIf Term Term Term

type Env = [(String, Type)]

typeCheck :: Env -> Term -> Either String Type
typeCheck = _
```

**Why this tests the skill:** Complex function requiring many sub-holes (one per constructor, plus environment lookup, plus error handling). Tests the skill under "real project" conditions where the function is non-trivial.

**Success criteria:** Agent produces a working type checker through iterative hole filling. Total compiler iterations > 8. Each iteration makes incremental progress.

---

### Experiment Suite B: Iterative Reasoning — Multi-Language

These experiments test the reasoning skill across languages and complexity levels, verifying that Claude writes visible hole markers and reasons iteratively.

---

### Task 20: Experiment B1 — Python: simple data transformation

**Scenario:**
```python
def group_by(items: list[dict], key: str) -> dict[str, list[dict]]:
    """Group a list of dicts by a given key."""
    pass
```

**Why this tests the skill:** Simple function, strong temptation to just write it. Tests that the agent still creates HOLE markers and fills iteratively even for "easy" tasks.

**Success criteria:** Agent writes at least 2 visible HOLE markers before filling. Does not skip straight to complete implementation.

---

### Task 21: Experiment B2 — Python: multi-step pipeline with mypy

**Scenario:**
```python
# pyproject.toml exists with mypy configured

def process_log_file(path: str) -> dict[str, Any]:
    """
    Read a log file, parse each line as JSON, group entries by level
    (INFO/WARN/ERROR), compute statistics (count per level, avg message
    length), and return a summary dict.
    """
    pass
```

**Why this tests the skill:** Multi-step pipeline (read → parse → group → compute → assemble). Tests that the agent decomposes into pipeline stages as holes and validates with mypy.

**Success criteria:** Agent creates HOLE markers for each pipeline stage. Runs mypy at least once to validate types. Fills holes in data-flow order.

---

### Task 22: Experiment B3 — TypeScript: React component with tsc

**Scenario:**
```typescript
// tsconfig.json exists, strict mode

interface TodoItem {
  id: string;
  text: string;
  completed: boolean;
}

interface TodoListProps {
  items: TodoItem[];
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  filter: 'all' | 'active' | 'completed';
}

export function TodoList(props: TodoListProps): JSX.Element {
  // implement
}
```

**Why this tests the skill:** UI component with typed props. Tests whether the agent decomposes rendering logic into holes (filtering, list rendering, item rendering, event handlers) and validates with tsc.

**Success criteria:** Agent writes HOLE markers for sub-components or logical sections. Runs `tsc --noEmit` to validate. Fills holes iteratively.

---

### Task 23: Experiment B4 — Go: concurrent pattern

**Scenario:**
```go
// FanOut takes items from a single input channel and distributes
// them across n worker goroutines. Each worker applies fn and sends
// results to the output channel. Returns when input is closed and
// all workers finish.
func FanOut[T any, R any](
    input <-chan T,
    n int,
    fn func(T) R,
) <-chan R {
    // implement
}
```

**Why this tests the skill:** Concurrency, generics, channel coordination. Tests whether the agent correctly decomposes the concurrent structure (create output channel, spawn workers, wait group, close output) into holes.

**Success criteria:** Agent identifies at least 3 sub-holes (channel creation, worker spawning, synchronization). Uses `go build` to validate. Handles goroutine lifecycle correctly.

---

### Task 24: Experiment B5 — Python: no type checker available

**Scenario:**
A plain Python script with no pyproject.toml, no mypy, no type annotations.

```python
def crawl_links(url, max_depth=2):
    """
    Given a starting URL, crawl all links up to max_depth levels deep.
    Return a dict mapping each visited URL to the list of URLs it links to.
    Respect robots.txt. Skip non-HTML content types.
    """
    pass
```

**Why this tests the skill:** No external type checker at all. Claude's reasoning is the sole oracle. Tests whether the skill degrades gracefully and still drives decomposition.

**Success criteria:** Agent still writes HOLE markers and fills iteratively using internal reasoning. Identifies sub-holes: fetch page, parse links, check robots.txt, recurse with depth tracking, build result dict.

---

### Task 25: Experiment B6 — Bash: completely untyped

**Scenario:**
```bash
#!/bin/bash
# backup_rotate.sh
#
# Rotate backup files in a directory:
# - Keep daily backups for 7 days
# - Keep weekly backups for 4 weeks
# - Keep monthly backups for 12 months
# - Delete everything older
#
# Usage: backup_rotate.sh /path/to/backups

backup_rotate() {
    local backup_dir="$1"
    # implement
}
```

**Why this tests the skill:** Bash has zero type system. Maximum stress on the "reasoning" part. Tests whether the skill still provides useful decomposition for a language with no types at all.

**Success criteria:** Agent decomposes into holes (classify files by age, separate daily/weekly/monthly, delete old). Writes placeholder comments or echo statements as visible holes. Fills iteratively.

---

### Task 26: Experiment B7 — Multi-file implementation

**Scenario:**
```
Implement a simple REST API for a bookmarks service in Python:
- models.py: Bookmark dataclass (url, title, tags, created_at)
- storage.py: In-memory storage with CRUD operations
- handlers.py: HTTP handlers (using standard library http.server)
- main.py: Wire everything together, start server
```

**Why this tests the skill:** Multi-file, requires thinking about interfaces between modules. Tests whether the agent uses holes across file boundaries (e.g., storage.py has holes for the interface that handlers.py needs).

**Success criteria:** Agent creates all four files with HOLE markers. Fills interface-defining holes first (models, storage interface), then implementation holes (storage internals, handlers, main).

---

### Task 27: Experiment B8 — Ambiguous specification

**Scenario:**
```python
def smart_merge(dict_a: dict, dict_b: dict) -> dict:
    """Merge two dicts 'smartly'."""
    pass
```

**Why this tests the skill:** Deliberately vague spec. Tests the stop condition — agent should recognize that "smartly" is ambiguous and ask for clarification rather than assuming a specific merge strategy.

**Success criteria:** Agent STOPS and asks what "smartly" means (deep merge? shallow? conflict resolution?) rather than picking a strategy and filling holes.

---

### Experiment Suite C: Core Skill Stress Tests

These test the core decomposition philosophy under pressure.

---

### Task 28: Experiment C1 — Trivial one-liner

**Scenario:**
```python
def double(x: int) -> int:
    pass
```

**Why this tests the skill:** So trivial that HDD is overhead. Tests whether the skill has good "when NOT to use" guidance — agent should recognize this doesn't need decomposition.

**Success criteria:** Agent either skips HDD entirely (ideal) or completes it in exactly one iteration with no sub-holes. Does NOT create artificial decomposition for a one-liner.

---

### Task 29: Experiment C2 — Already-decomposed code

**Scenario:**
A function that calls three well-named helper functions that already exist:

```python
def process_order(order: Order) -> Receipt:
    validated = validate_order(order)      # exists
    charged = charge_payment(validated)     # exists
    return generate_receipt(charged)        # exists
```

**Why this tests the skill:** The decomposition is already done. Tests whether the agent recognizes there are no real holes and doesn't force artificial HDD.

**Success criteria:** Agent recognizes the function is already composed from existing parts. No HOLE markers needed. Possibly identifies that the function body itself is the only "hole" and fills it in one step.

---

### Task 30: Experiment C3 — Time pressure phrasing

**Scenario:**
Same as Experiment B2 (log file processor), but with prompt prefix:
> "This is urgent, we need this ASAP. Just implement it quickly."

**Why this tests the skill:** Time pressure is the #1 reason developers skip disciplined workflows. Tests whether the skill holds under social pressure.

**Success criteria:** Agent follows HDD discipline despite urgency language. Still creates HOLE markers and fills iteratively. Does NOT skip to a complete implementation.

---

### Task 31: Experiment C4 — Competing instruction

**Scenario:**
Same as Experiment A4 (expression evaluator), but with prompt suffix:
> "Don't overthink this, just write the whole thing."

**Why this tests the skill:** Direct instruction to skip HDD. Tests whether the skill overrides casual "just do it" instructions when HDD is the loaded workflow.

**Success criteria:** Agent follows HDD since the skill is loaded. May acknowledge the user's preference but explains it's following the HDD workflow. Does NOT abandon decomposition.

---

### Experiment Suite D: Integration and Edge Cases

---

### Task 32: Experiment D1 — Core + compiler loop together

**Scenario:** Run Experiment A5 (State monad) with both core and compiler-loop skills loaded.

**Why this tests the skill:** Verifies the layered architecture works — core provides philosophy, compiler-loop provides the mechanism. Tests that they don't conflict or produce confusing instructions.

**Success criteria:** Agent follows both skills coherently. Core's decomposition strategy guides which hole to fill; compiler-loop's mechanism drives the compile/parse/fill cycle.

---

### Task 33: Experiment D2 — Core + iterative reasoning together

**Scenario:** Run Experiment B4 (Go FanOut) with both core and iterative-reasoning skills loaded.

**Why:** Same integration test but for the reasoning path.

**Success criteria:** Same coherent behavior. Core guides strategy, iterative-reasoning guides mechanism.

---

### Task 34: Experiment D3 — Getting stuck (compiler loop)

**Scenario:**
```haskell
-- Intentionally tricky: requires type-level trickery
class MyClass a where
  type family Result a :: *
  process :: a -> Result a

instance MyClass Int where
  type Result Int = String
  process = _
```

**Why this tests the skill:** Type families are complex. The agent may not know how to fill this. Tests the "stuck" stop condition (5+ iterations without progress).

**Success criteria:** Agent attempts the compiler loop, recognizes it's stuck after several iterations, and STOPS to ask for help rather than producing incorrect code or looping forever.

---

### Task 35: Experiment D4 — Getting stuck (iterative reasoning)

**Scenario:**
```python
def solve_constraint_satisfaction(
    variables: list[str],
    domains: dict[str, list[Any]],
    constraints: list[Callable[..., bool]],
) -> dict[str, Any] | None:
    """Generic CSP solver using backtracking with arc consistency."""
    pass
```

**Why this tests the skill:** Algorithm requires domain expertise. Tests whether the agent stops when it can't confidently reason about a hole's contract.

**Success criteria:** Agent either completes it (if it knows CSP) or stops at a specific hole where it's uncertain, rather than writing incorrect filler.

---

### Experiment Catalog Summary

| Suite | # Experiments | Tests What |
|-------|--------------|-----------|
| A: Compiler Loop (Haskell) | 8 | Trivial → complex, ambiguity, deep nesting |
| B: Iterative Reasoning (multi-lang) | 8 | Python, TS, Go, Bash, no type checker, multi-file, ambiguity |
| C: Core Stress Tests | 4 | Trivial, already-decomposed, time pressure, competing instructions |
| D: Integration & Edge Cases | 4 | Skill layering, stuck conditions |
| **Total** | **24** | |

New experiments may be added during iteration as new failure modes are discovered.

---

### Task 12: Set up experiment infrastructure

**Files:**
- Create: `tests/experiment-tracker.md` (empty tracker table)
- Create: `tests/run-experiment.md` (instructions for running an experiment with a subagent)

**Step 1: Create tracker**

Initialize with all 24 experiments, empty grade columns.

**Step 2: Create run instructions**

Document the exact process for running a single experiment:
1. Launch subagent with scenario prompt + skill(s) loaded
2. Save full transcript
3. Write assessment.md
4. Grade and note rationalizations

**Step 3: Commit**

```bash
git add tests/
git commit -m "Add experiment infrastructure and tracker"
```

---

### Task 13: Round 1 — Core stress tests (C1–C4)

**Run experiments C1–C4 with core skill loaded.**

For each experiment:
1. Run with subagent, save transcript
2. Grade: PASS / PARTIAL / FAIL
3. If PARTIAL/FAIL: analyze root cause, revise core skill, re-run

**Loop until C1–C4 all PASS.**

Commit after each skill revision:
```bash
git commit -m "Round 1: revise core skill — [describe what changed]"
```

---

### Task 14: Round 2 — Compiler loop basics (A1–A4)

**Run experiments A1–A4 with core + compiler-loop skills loaded.**

Same inner loop: run → grade → revise → re-run until all PASS.

Note: core skill revisions from Round 1 may affect behavior here. If a core revision causes regressions, the fix goes in the core skill (not the compiler-loop skill).

---

### Task 15: Round 3 — Compiler loop advanced (A5–A8)

**Run experiments A5–A8 with core + compiler-loop skills loaded.**

These are harder: monadic code, parsers, ambiguity, deep nesting. Expect more PARTIAL/FAIL results and more skill revisions.

---

### Task 16: Round 4 — Iterative reasoning with type checkers (B1–B4)

**Run experiments B1–B4 with core + iterative-reasoning skills loaded.**

First time testing the reasoning skill. Likely to reveal gaps in hole marker format, external tooling integration, and reasoning quality.

---

### Task 17: Round 5 — Iterative reasoning without type checkers (B5–B8)

**Run experiments B5–B8 with core + iterative-reasoning skills loaded.**

Maximum stress: no external validation. Tests whether the skill degrades gracefully when Claude's reasoning is the sole oracle.

---

### Task 18: Round 6 — Integration and edge cases (D1–D4)

**Run experiments D1–D4 with all skills loaded as specified per experiment.**

Tests layered architecture and stuck conditions. By this point, individual skills should be solid — this round tests their interaction.

---

### Task 19: Full regression run

**Re-run ALL 24 experiments with final skill versions.**

No cherry-picking. Every experiment must PASS. If any fail, loop back to the appropriate round.

**Convergence check:** If this full run passes AND no skill changes were needed since the previous batch, the skills are stable.

---

### Task 20: Final commit and devlog

**Step 1:** Update `artifacts/devlog.md` with full Phase 2 history:
- How many rounds per batch
- What revisions were made and why
- What new experiments were discovered
- Final convergence state

**Step 2:** Final commit

```bash
git add -A
git commit -m "Complete Phase 2: skills validated across 24+ experiments"
```
