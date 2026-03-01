# Hole Driven Development Skills — Demo Results

Phase 1 demonstration of three HDD skills for Claude Code. Each skill was tested using RED-GREEN-REFACTOR: baseline without skill, then with skill loaded.

## What is Hole Driven Development?

Hole Driven Development (HDD) is a top-down programming technique from Haskell. Instead of writing a complete implementation, you:

1. Start with the outermost structure
2. Leave **holes** for unknown sub-problems
3. Let the type checker (or your reasoning) tell you what each hole needs
4. Fill one hole at a time, possibly introducing smaller holes
5. Repeat until no holes remain

These skills teach Claude to follow this discipline.

## The Three Skills

| Skill | Role | Oracle |
|-------|------|--------|
| `hole-driven-development-core` | Philosophy — decompose, holes visible in file, one at a time, most constrained first | Abstract |
| `hole-driven-development` | Compiler loop — compile, read diagnostics, fill, repeat | GHC / compiler |
| `hole-driven-development-iterative-reasoning` | Claude reasons about each hole's contract, writes visible markers | Claude's reasoning + optional type checker |

## Demo 1: Core Skill — Python TOC Generator

**Task:** Implement `generate_toc(markdown: str) -> str` — parse headings, generate nested TOC with links, handle duplicates.

### Without skill (baseline)

Agent wrote everything in a single function, in a single pass. 5 tool calls.

```python
def generate_toc(markdown: str) -> str:
    lines = markdown.splitlines()
    toc_entries = []
    slug_counts: dict[str, int] = {}
    for line in lines:
        match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if not match:
            continue
        level = len(match.group(1))
        text = match.group(2).strip()
        slug = text.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug).strip("-")
        if slug in slug_counts:
            slug_counts[slug] += 1
            slug = f"{slug}-{slug_counts[slug]}"
        else:
            slug_counts[slug] = 0
        indent = "  " * (level - 1)
        toc_entries.append(f"{indent}- [{text}](#{slug})")
    return "\n".join(toc_entries)
```

All logic inlined. No decomposition. Written all at once.

### With skill

Agent decomposed into 4 holes, filled one at a time. 19 tool calls.

**Step 1 — Skeleton with holes:**
```python
def generate_toc(markdown: str) -> str:
    headings = _extract_headings(markdown)          # HOLE_1
    toc_entries: list[str] = []
    slug_counts: dict[str, int] = {}
    for level, text in headings:
        slug = _make_slug(text)                     # HOLE_2
        slug = _deduplicate_slug(slug, slug_counts) # HOLE_3
        toc_entries.append(_format_entry(level, text, slug))  # HOLE_4
    return "\n".join(toc_entries)
```

Each helper started as `raise NotImplementedError("HOLE: ...")`.

**Fill order (most constrained first):**

| Order | Hole | Rationale |
|-------|------|-----------|
| 1st | `_format_entry` | Pure string formatting, zero ambiguity |
| 2nd | `_deduplicate_slug` | Mechanical counter logic |
| 3rd | `_extract_headings` | Regex determined by spec |
| 4th | `_make_slug` | Least constrained — multiple valid algorithms |

**Result:** Same output. Better structure — each sub-problem is a named, testable function.

### Key metrics

| Metric | Baseline | With skill |
|--------|----------|-----------|
| Tool calls | 5 | 19 |
| Decomposition | None | 4 holes |
| Visible holes in file | Never | Yes |
| Code structure | Monolithic | 5 focused functions |

---

## Demo 2: Compiler Loop — Haskell myFoldr

**Task:** Implement `myFoldr :: (a -> b -> b) -> b -> [a] -> b` using GHC's typed hole system.

### The compiler loop in action

**Starting point:**
```haskell
myFoldr :: (a -> b -> b) -> b -> [a] -> b
myFoldr = _
```

**Cycle 1 — Initial compile:**
```
Found hole: _ :: (a -> b -> b) -> b -> [a] -> b
Valid hole fits: myFoldr, foldr
```
Agent introduced pattern matching with named holes:
```haskell
myFoldr f z []     = _empty
myFoldr f z (x:xs) = _cons
```

**Cycle 2 — Two holes:**
```
_empty :: b       Valid fits: z
_cons  :: b       Valid fits: z (misleading!)
```
Most constrained: `_empty` (single valid fit). Filled with `z`.

**Cycle 3 — One hole remains:**
```
_cons :: b
Relevant bindings: f :: a -> b -> b, x :: a, xs :: [a], myFoldr :: ...
```
Agent decomposed into `f x _rest`, introducing a sub-hole.

**Cycle 4 — Sub-hole:**
```
_rest :: b
Relevant bindings: myFoldr, xs, z, f
```
Filled with `myFoldr f z xs` (recursive call).

**Cycle 5 — Compilation succeeds.**
```haskell
myFoldr f z []     = z
myFoldr f z (x:xs) = f x (myFoldr f z xs)
```

### Key metrics

| Metric | Value |
|--------|-------|
| Compile cycles | 5 |
| Holes filled | 4 (including sub-hole `_rest`) |
| Named holes used | `_empty`, `_cons`, `_rest` |
| Misleading fits avoided | 1 (`z` for recursive case) |

---

## Demo 3: Iterative Reasoning — Python CSV Parser

**Task:** Implement `parse_csv(text: str) -> list[dict[str, str]]` — handle quoted fields with commas.

### Without skill (baseline)

Agent wrote 17-line complete implementation in one pass. 7 tool calls. No decomposition visible.

### With skill

Agent decomposed into 3 holes + 1 sub-hole. 15 tool calls.

**Step 1 — Skeleton with holes:**
```python
def parse_csv(text: str) -> list[dict[str, str]]:
    raise NotImplementedError("HOLE_1: split text into rows # expects: list[str]")
    raise NotImplementedError("HOLE_2: extract headers from first row # expects: list[str]")
    raise NotImplementedError("HOLE_3: parse each data row into dict # expects: list[dict[str, str]]")
```

**Step 2 — Fill HOLE_1** (most constrained — everything depends on it):
```python
rows = text.strip().split('\n')
if not rows:
    return []
```

**Step 3 — Fill HOLE_2** (introduced sub-hole HOLE_2a):
```python
def parse_row(line: str) -> list[str]:
    raise NotImplementedError("HOLE_2a: character-by-character field parsing # expects: list[str]")
headers = parse_row(rows[0])
```

**Step 4 — Fill HOLE_2a** (the core parsing logic):
```python
fields = []
current = []
in_quotes = False
for ch in line:
    if ch == '"':
        in_quotes = not in_quotes
    elif ch == ',' and not in_quotes:
        fields.append(''.join(current))
        current = []
    else:
        current.append(ch)
fields.append(''.join(current))
return fields
```

**Step 5 — Fill HOLE_3** (final assembly):
```python
return [dict(zip(headers, parse_row(row))) for row in rows[1:]]
```

### Key metrics

| Metric | Baseline | With skill |
|--------|----------|-----------|
| Tool calls | 7 | 15 |
| Decomposition | None | 3 holes + 1 sub-hole |
| Visible holes in file | Never | Yes |
| Contract reasoning | Implicit | Explicit per hole |

---

## Key Findings

### What the skills change

1. **Visible decomposition.** Without skills, agents decompose mentally but write complete code. With skills, holes live in the file — the human watches the skeleton evolve.

2. **One hole at a time.** Without skills, agents batch-write. With skills, they fill exactly one hole per iteration, re-assessing after each fill.

3. **Constraint-driven ordering.** Agents naturally pick holes in reading order. The skill redirects toward most-constrained-first, which reduces errors.

4. **Better code structure.** The HDD process naturally produces modular code (named helpers, clear interfaces) vs. monolithic implementations.

### Critical skill refinements discovered during testing

| Issue found | Refinement added |
|-------------|-----------------|
| Agent kept holes in head, wrote final code | "Holes must be visible — write to the file" |
| Agent used bare `_` for multiple holes | "Use named holes (`_name`)" |
| Agent under-decomposed (2 holes for 4 requirements) | "Each distinct concern gets a hole" |

### Architecture validation

The three-layer architecture works:
- Core provides philosophy (decompose, visible holes, one at a time)
- Compiler-loop adds mechanism (compile, read diagnostics, fill)
- Iterative-reasoning adds mechanism (reason about contract, write markers)
- Core + extending skill compose cleanly — no conflicts

---

## Reproduction

All test artifacts are in `tests/`:

```
tests/
├── hole-driven-development-core/
│   ├── scenario-1-decomposition.md
│   └── results/
│       ├── baseline-toc.py          # Without skill
│       ├── refactor-toc.py          # With skill (final)
│       └── baseline-assessment.md
├── hole-driven-development/
│   ├── scenario-1-haskell-holes.md
│   ├── test-project/Lib.hs         # Starting point (typed hole)
│   └── results/
│       ├── baseline-Lib.hs
│       ├── green-Lib.hs
│       ├── integration-Lib.hs
│       └── green-assessment.md
└── hole-driven-development-iterative-reasoning/
    ├── scenario-1-python-holes.md
    └── results/
        ├── baseline-csv.py
        ├── green-csv.py
        ├── integration-csv.py
        └── green-assessment.md
```
