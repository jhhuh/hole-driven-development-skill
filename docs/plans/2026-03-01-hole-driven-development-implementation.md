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
