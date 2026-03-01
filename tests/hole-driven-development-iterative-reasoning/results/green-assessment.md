# GREEN Assessment: Iterative-Reasoning Skill — Scenario 1 (CSV Parser)

## Grade: PASS

## Behavior observed

Agent followed the iterative-reasoning loop:
- Step 1: Wrote skeleton with 2 HOLE markers (`NotImplementedError`)
  - HOLE_1: parse_row — parse a single row respecting quotes (contract: `str -> list[str]`)
  - HOLE_2: header mapping — use parse_row to build list of dicts (contract: `list[dict[str, str]]`)
- Step 2: Filled HOLE_1 first (most constrained — HOLE_2 depends on it)
  - Stated contract before filling: produces `list[str]`, inputs: single line string
  - Reasoned about quote-handling constraint
- Step 3: Filled HOLE_2 (now unblocked)
  - Stated contract: produces `list[dict[str, str]]`, uses `parse_row` and `rows`
- 14 tool calls total (vs 7 in baseline), indicating iterative file edits

## Comparison to baseline

| Aspect | Baseline | GREEN (skill loaded) |
|--------|----------|---------------------|
| Decomposition | None — all at once | 2 holes, filled iteratively |
| Visible holes in file | Never | Yes — NotImplementedError stubs |
| Contract reasoning | Implicit | Explicit per hole |
| Tool calls | 7 | 14 (more iterations) |

## Potential improvement

Only 2 holes for a 4-requirement spec. Could have been more granular (e.g., row splitting, empty handling, quote parsing, header mapping as separate holes). But 2 holes is defensible — parse_row IS the hard sub-problem, the rest is glue.

## Skill revision needed

Minor — the skill could emphasize that each distinct requirement or concern should map to at least one hole. But forcing over-decomposition on simple problems would violate YAGNI.

## Rationalizations observed

None — agent followed the process.
