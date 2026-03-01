# D4: CSP Solver - HDD Assessment

## 1. Did you complete it or get stuck?

**Completed.** The solver was fully implemented and verified against 6 test cases:
graph coloring, unsatisfiable instances, unary constraints, 4-queens, no constraints,
and ternary constraints. No holes caused enough uncertainty to trigger a stop-and-ask.

## 2. How many holes did you create?

**6 holes total**, across two decomposition phases:

### Phase 1 (initial skeleton): 3 holes
| Hole | Description | Status |
|------|-------------|--------|
| HOLE_1 | Extract variable scopes from constraints via `inspect.signature` | Filled |
| HOLE_2 | AC-3 arc consistency (prune domains, detect wipeout) | Decomposed further |
| HOLE_3 | Backtracking search with forward checking via AC-3 | Decomposed further |

### Phase 2 (refinement): 3 sub-holes
| Hole | Parent | Description | Status |
|------|--------|-------------|--------|
| HOLE_2a | HOLE_2 | Process arc queue: revise domains and propagate | Filled |
| HOLE_3a | HOLE_3 | Consistency check (all constraints involving var vs assignment) | Filled |
| HOLE_3b | HOLE_3 | MRV variable selection heuristic | Filled |
| HOLE_3c | HOLE_3 | Main backtracking loop with MAC propagation | Filled |

(7 holes if counting HOLE_3c separately from the 3 sub-holes, but HOLE_3 itself was
replaced by HOLE_3a/3b/3c, so the total unique holes filled is 6.)

## 3. Which hole (if any) caused uncertainty?

**HOLE_2 / HOLE_2a (AC-3 implementation)** required the most careful reasoning:

- **Design decision**: How to handle non-binary constraints with AC-3 (which is
  inherently a binary constraint algorithm). Resolution: unary constraints get node
  consistency filtering; ternary+ constraints are checked only during backtracking.
  This is the standard textbook approach and did not require stopping to ask.

- **Argument ordering**: When processing arc (Xi, Xj) for a constraint with scope
  [A, B], the argument order depends on whether Xi=A (call as c(vi, vj)) or Xi=B
  (call as c(vj, vi)). This required careful thought but was resolvable from the
  constraint scope metadata.

- **Constraint signature**: The `Callable[..., bool]` type hint was initially ambiguous
  regarding how constraints map to variables. The `inspect.signature` approach
  (HOLE_1) resolved this cleanly -- constraint parameter names must match variable
  names. This is a reasonable convention that makes the API ergonomic for callers.

No hole triggered the "stuck for 5+ iterations" threshold.

## 4. Total tool calls

**17 tool calls:**
- 2 Bash (directory check + mkdir)
- 1 Write (initial skeleton)
- 1 Read + 6 Edit (filling holes iteratively)
- 2 Bash (test execution: finding python, running tests)
- 1 Write (test file, then removed)
- 1 Bash (cleanup test file)
- 1 Read (verify final state)
- 1 Write (this assessment)
