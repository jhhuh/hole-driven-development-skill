# Iterative Reasoning Skill

You are the type checker. Decompose implementation into visible hole markers, reason about each hole's contract, and fill them one at a time.

**Requires:** [`hole-driven-development-core`](core.md)

## When to Use

- Implementing in any language, especially those without typed holes
- HDD discipline for dynamically typed languages (Python, JS, Go, Bash)
- When no compiler with hole diagnostics is available

## Hole Markers

Write real, language-appropriate placeholder code:

| Language | Hole marker |
|----------|------------|
| Python | `raise NotImplementedError("HOLE_N: <description> # expects: <type>")` |
| JavaScript/TS | `throw new Error("HOLE_N: <description> // expects: <type>")` |
| Go | `panic("HOLE_N: <description> // expects: <type>")` |
| Bash | `echo "HOLE_N: <description>" && exit 1` |

Each hole has: a number, a description, and what type/contract it fulfills.

## The Reasoning Loop

```
1. Receive intention
2. Write skeleton to the file with HOLE markers for each sub-problem
3. PICK the most constrained hole
4. REASON about what it needs:
   - What type/value does it produce?
   - What inputs are available in scope?
   - What constraints apply?
5. FILL exactly one hole — introduce sub-holes if complex
6. VALIDATE (optional): run type checker if available
7. VERIFY cross-hole interactions: for each filled hole sharing state with this fill:
   - Shared mutable state: is access properly synchronized?
   - Resource lifecycle: are acquire/release scopes correct across hole boundaries?
   - Error/cancellation paths: do they propagate correctly to other holes?
   Fix any issue before continuing.
8. Repeat from 3 until no holes remain
9. REVIEW-ALL: before declaring done, re-read the complete implementation:
   - State transitions that span multiple fills
   - Resource acquired in one fill, released in another
   - Error paths that cross fill boundaries
   - Loop invariants depending on multiple fills
   Fix any systemic bug the per-hole VERIFY could not catch.
```

**Each distinct concern gets a hole.** N requirements → at least N holes.

**Reason before filling.** State: what it produces, what's available, why the fill is correct.

**Verify after filling.** Cross-cutting concerns (concurrency, resource lifecycle, error handling) don't decompose into independent holes. After each fill, check interactions with previously filled code.

**When NOT to decompose further.** Algorithms with tightly coupled state machines (dual-cursor walks, FSMs with shared transition state) should stay as a single hole. Use internal comments to mark structure, but don't split the state machine across sub-holes.

## External Validation (Optional)

| Language | Type checker | Detection |
|----------|-------------|-----------|
| Python | `mypy`, `pyright` | `pyproject.toml`, `.py` |
| TypeScript | `tsc --noEmit` | `tsconfig.json`, `.ts` |
| Go | `go build` | `go.mod`, `.go` |

## Example: CSV Parser

**Step 1 — Skeleton:**
```python
def parse_csv(text: str) -> list[dict[str, str]]:
    raise NotImplementedError("HOLE_1: split text into rows # expects: list[str]")
    raise NotImplementedError("HOLE_2: extract headers # expects: list[str]")
    raise NotImplementedError("HOLE_3: parse data rows into dicts # expects: list[dict[str, str]]")
```

**Step 2 — Fill HOLE_1** (most constrained — everything depends on it):
```python
rows = text.strip().split('\n')
if not rows:
    return []
```

**Step 3 — Fill HOLE_2** (introduces sub-hole HOLE_2a for parsing logic):
```python
def parse_row(line: str) -> list[str]:
    raise NotImplementedError("HOLE_2a: character-by-character field parsing")
headers = parse_row(rows[0])
```

**Step 4 — Fill HOLE_2a** (core parsing with quote handling).

**Step 5 — Fill HOLE_3** (final assembly):
```python
return [dict(zip(headers, parse_row(row))) for row in rows[1:]]
```
