---
name: hole-driven-development-iterative-reasoning
description: Use when implementing in any language using top-down decomposition with visible hole markers, where Claude reasons about each hole's contract and fills iteratively
---

# Hole Driven Development — Iterative Reasoning

**REQUIRED BACKGROUND:** `hole-driven-development-core`

## Overview

You are the type checker. Decompose implementation into visible hole markers in the file, reason about each hole's contract (inputs, outputs, constraints), and fill them one at a time.

**Core principle:** Make your reasoning visible. Holes live in the file, not in your head.

## When to Use

- Implementing in any language, especially those without typed holes
- HDD discipline for dynamically typed languages (Python, JS, Go, Bash)
- When no compiler with hole diagnostics is available

## Hole Markers

Write real, language-appropriate placeholder code that makes holes visible in the editor:

| Language | Hole marker |
|----------|------------|
| Python | `raise NotImplementedError("HOLE_N: <description> # expects: <type>")` |
| JavaScript/TypeScript | `throw new Error("HOLE_N: <description> // expects: <type>")` |
| Go | `panic("HOLE_N: <description> // expects: <type>")` |
| Bash | `echo "HOLE_N: <description>" && exit 1` |
| Other | Comment: `/* HOLE_N: <description> — expects: <type> */` |

Each hole has: a number, a description of what it does, and what type/contract it fulfills.

## The Reasoning Loop

```
1. Receive intention
2. Write skeleton to the file with HOLE markers for each sub-problem
3. PICK the most constrained hole
4. REASON about what it needs:
   - What type/value does it produce?
   - What inputs are available in scope?
   - What constraints apply?
5. FILL exactly one hole in the file — introduce sub-holes if complex
6. VALIDATE (optional): run type checker if available (see table below)
7. Repeat from 3 until no holes remain
```

**One hole per iteration.** Fill one, reassess, then pick the next.

**Each distinct concern gets a hole.** When the spec has N distinct requirements or sub-problems, the skeleton should have at least N holes. Don't collapse multiple concerns into one hole — that defeats the purpose of decomposition.

**Reason before filling.** For each hole, explicitly state: what it needs to produce, what it has available, and why your fill is correct. Do not skip this reasoning step.

## External Validation (Optional)

When a type checker is available, run it after filling to catch errors:

| Language | Type checker | Detection |
|----------|-------------|-----------|
| Python | `mypy`, `pyright` | `pyproject.toml`, `.py` |
| TypeScript | `tsc --noEmit` | `tsconfig.json`, `.ts` |
| Go | `go build` | `go.mod`, `.go` |

If no type checker is available, your reasoning is the sole oracle. Be more careful with constraint analysis.

## Autonomy

Run the loop autonomously. **Stop only when:**

- **Done:** No holes remain and code satisfies the intention.
- **Ambiguous:** A hole's contract is unclear — multiple valid approaches with different semantics. Surface options to the human.
- **Stuck:** 5+ iterations on the same hole without progress. Ask for help.

## Red Flags — STOP

- Writing complete implementation without creating holes first
- Keeping holes in your head — every hole must be in the file
- Filling multiple holes in one step
- Skipping the reasoning step ("obvious what goes here")
- Not stating the hole's contract before filling it

**If you catch yourself doing any of these: STOP. Write holes to the file first.**
