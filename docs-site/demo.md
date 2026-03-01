# Demo Results

Phase 1 demonstration of three HDD skills for Claude Code. Each skill was tested using RED-GREEN-REFACTOR: baseline without skill, then with skill loaded.

## Demo 1: Core Skill — Python TOC Generator

**Task:** Implement `generate_toc(markdown: str) -> str` — parse headings, generate nested TOC with links, handle duplicates.

### Without skill (baseline)

Agent wrote everything in a single function, in a single pass. 5 tool calls. All logic inlined, no decomposition.

### With skill

Agent decomposed into 4 holes, filled one at a time. 19 tool calls.

**Skeleton with holes:**
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

### Metrics

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

**Cycle 1:** Compile → hole type `(a -> b -> b) -> b -> [a] -> b`. Introduce pattern matching with named holes `_empty`, `_cons`.

**Cycle 2:** `_empty :: b` (fits: `z`), `_cons :: b` (fits: `z` — misleading!). Fill `_empty` with `z`.

**Cycle 3:** `_cons :: b`, bindings show `f :: a -> b -> b`, `x :: a`, `xs :: [a]`. Decompose into `f x _rest`.

**Cycle 4:** `_rest :: b`, bindings include `myFoldr`. Fill with `myFoldr f z xs`.

**Cycle 5:** Compilation succeeds.

```haskell
myFoldr f z []     = z
myFoldr f z (x:xs) = f x (myFoldr f z xs)
```

### Metrics

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

**Skeleton → fill HOLE_1 → fill HOLE_2 (introduces sub-hole HOLE_2a) → fill HOLE_2a → fill HOLE_3.**

### Metrics

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

The three-layer architecture composes cleanly:

- Core provides philosophy (decompose, visible holes, one at a time)
- Compiler-loop adds mechanism (compile, read diagnostics, fill)
- Iterative-reasoning adds mechanism (reason about contract, write markers)
- No conflicts when combining core + extending skill
