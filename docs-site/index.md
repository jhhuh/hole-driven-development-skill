# Hole Driven Development — Claude Code Skills

Three composable skills that teach Claude Code agents to implement code using **Hole Driven Development** (HDD), a top-down programming technique from Haskell.

Instead of writing complete implementations in one pass, the agent:

1. Starts with the outermost structure
2. Leaves **holes** for unknown sub-problems
3. Lets the type checker (or its own reasoning) reveal what each hole needs
4. Fills one hole at a time, most constrained first
5. Repeats until no holes remain

## Skills

| Skill | What it does | Oracle |
|-------|-------------|--------|
| [`hole-driven-development-core`](skills/core.md) | Philosophy — decompose, visible holes, one at a time, most constrained first | Abstract |
| [`hole-driven-development`](skills/compiler-loop.md) | Compiler loop — compile, read diagnostics, fill, repeat | GHC / compiler |
| [`hole-driven-development-iterative-reasoning`](skills/iterative-reasoning.md) | Claude reasons about each hole's contract, writes visible markers | Claude's reasoning + optional type checker |

## Architecture

Three-layer, composable:

```
hole-driven-development-core          ← philosophy (always loaded)
├── hole-driven-development           ← extends with compiler feedback loop
└── hole-driven-development-iterative-reasoning  ← extends with reasoning loop
```

The core skill defines the HDD discipline. Each extending skill adds a mechanism for determining what a hole needs — either a real compiler or Claude's own reasoning.

## Installation

Copy the `skills/` directory into your Claude Code skills location:

```bash
# Per-project
cp -r skills/ your-project/.claude/skills/

# Or user-wide
cp -r skills/ ~/.claude/skills/
```

Each skill has a YAML frontmatter with `name` and `description` that Claude Code uses for discovery.

## Quick Start

### Compiler Loop (Haskell)

Load `hole-driven-development`. Give Claude a type signature with a hole:

```haskell
myFoldr :: (a -> b -> b) -> b -> [a] -> b
myFoldr = _
```

Claude autonomously compiles, reads diagnostics, and fills holes one at a time until compilation succeeds.

### Iterative Reasoning (any language)

Load `hole-driven-development-iterative-reasoning`. Ask Claude to implement a function:

> Implement `parse_csv(text: str) -> list[dict[str, str]]` — handle quoted fields.

Claude writes visible hole markers, reasons about each contract, and fills one at a time.

See the [Demo](demo.md) for detailed before/after comparisons.

## Supported Languages

**Compiler loop** (real typed holes):

- Haskell (GHC) — implemented
- Lean 4 — planned
- Rust — planned

**Iterative reasoning** (hole markers):

- Python, JavaScript/TypeScript, Go, Bash, and any other language
