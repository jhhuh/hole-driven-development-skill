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
| `hole-driven-development-core` | Philosophy — decompose, visible holes in file, one at a time, most constrained first | Abstract |
| `hole-driven-development` | Compiler loop — compile, read diagnostics, fill, repeat | GHC / compiler |
| `hole-driven-development-iterative-reasoning` | Claude reasons about each hole's contract, writes visible markers | Claude's reasoning + optional type checker |

### Architecture

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

## Usage

### Compiler Loop (Haskell)

Load `hole-driven-development` (which requires `hole-driven-development-core`). Give Claude a type signature with a hole:

```haskell
myFoldr :: (a -> b -> b) -> b -> [a] -> b
myFoldr = _
```

Claude will autonomously:
1. Compile → read `Found hole: _ :: (a -> b -> b) -> b -> [a] -> b`
2. Introduce pattern matching with named holes (`_empty`, `_cons`)
3. Fill most constrained first (`_empty` has one valid fit: `z`)
4. Decompose complex holes into sub-holes (`f x _rest`)
5. Compile until success

### Iterative Reasoning (any language)

Load `hole-driven-development-iterative-reasoning` (which requires `hole-driven-development-core`). Ask Claude to implement a function:

> Implement `parse_csv(text: str) -> list[dict[str, str]]` — handle quoted fields with commas.

Claude will:
1. Write a skeleton with visible hole markers:
   ```python
   def parse_csv(text: str) -> list[dict[str, str]]:
       raise NotImplementedError("HOLE_1: split text into rows # expects: list[str]")
       raise NotImplementedError("HOLE_2: extract headers # expects: list[str]")
       raise NotImplementedError("HOLE_3: parse each data row into dict # expects: list[dict[str, str]]")
   ```
2. Fill one hole at a time, reasoning about each contract
3. Introduce sub-holes when a fill is complex
4. Optionally validate with `mypy`/`pyright` if available

## Demo Results

Phase 1 testing used RED-GREEN-REFACTOR to validate each skill. Key findings:

### What the skills change

| Metric | Without skill | With skill |
|--------|--------------|------------|
| Decomposition | Mental (invisible) | Written to file |
| Filling strategy | All at once | One hole per iteration |
| Fill order | Reading order | Most constrained first |
| Code structure | Monolithic | Modular (named helpers) |

### Python TOC Generator (core skill)

| | Baseline | With skill |
|-|----------|------------|
| Tool calls | 5 | 19 |
| Holes | 0 (monolithic) | 4, filled iteratively |
| Structure | 1 function | 5 focused functions |

### Haskell myFoldr (compiler loop)

5 compile cycles, 4 holes filled (including sub-hole `_rest`), 1 misleading fit avoided.

### Python CSV Parser (iterative reasoning)

| | Baseline | With skill |
|-|----------|------------|
| Tool calls | 7 | 15 |
| Holes | 0 | 3 + 1 sub-hole |
| Contract reasoning | Implicit | Explicit per hole |

Full demo details: [`artifacts/demo.md`](artifacts/demo.md)

## Key Refinements Discovered During Testing

| Issue | Fix added to skill |
|-------|--------------------|
| Agent decomposed mentally, wrote final code | "Holes must be visible — write to the file" |
| Agent used bare `_` for multiple holes | "Use named holes (`_name`)" |
| Agent under-decomposed | "Each distinct concern gets a hole" |

## Supported Languages

**Compiler loop** (real typed holes):
- Haskell (GHC) — implemented
- Lean 4 — planned
- Rust — planned

**Iterative reasoning** (hole markers):
- Python, JavaScript/TypeScript, Go, Bash, and any other language

## Project Structure

```
skills/
├── hole-driven-development-core/SKILL.md
├── hole-driven-development/SKILL.md
└── hole-driven-development-iterative-reasoning/SKILL.md
tests/
├── hole-driven-development-core/
├── hole-driven-development/
└── hole-driven-development-iterative-reasoning/
artifacts/
├── demo.md
└── devlog.md
docs/plans/
├── 2026-03-01-hole-driven-development-design.md
└── 2026-03-01-hole-driven-development-implementation.md
```

## License

MIT
