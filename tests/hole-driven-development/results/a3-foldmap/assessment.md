# A3: myFoldMap -- Compiler Loop Assessment

## 1. Number of compile cycles: 3

| Cycle | Action | Result |
|-------|--------|--------|
| 1 | Named holes `_baseCase` and `_consCase`, compiled | Two typed hole errors; diagnostics collected |
| 2 | Filled `_baseCase` with `mempty`, compiled | One typed hole error remains (`_consCase`) |
| 3 | Filled `_consCase` with `f x <> myFoldMap f xs`, compiled | Success -- no errors |

## 2. Holes introduced and filled

| Hole | Introduced | Filled | Fill value |
|------|-----------|--------|------------|
| `_baseCase` | Cycle 1 (renamed from bare `_`) | Cycle 2 | `mempty` |
| `_consCase` | Cycle 1 (renamed from bare `_`) | Cycle 3 | `f x <> myFoldMap f xs` |

## 3. Most constrained hole: `_baseCase`

`_baseCase :: m` was the most constrained hole because:

- **Fewer relevant bindings**: The only binding in scope was `f :: a -> m`, but there was no value of type `a` to apply it to (the list was empty `[]`).
- **Single valid fill**: With the `Monoid m` constraint and no `a`-typed values available, the only way to produce an `m` is `mempty`. There is exactly one inhabitant that type-checks.
- **Contrast with `_consCase`**: The cons case had three bindings (`x :: a`, `xs :: [a]`, `f :: a -> m`) plus the recursive call, giving multiple ways to compose an expression of type `m`. It was less constrained because the compiler could not narrow it to a single choice.

## 4. Total tool calls: 7

| # | Tool | Purpose |
|---|------|---------|
| 1 | Read | Read initial file |
| 2 | Edit | Name holes (`_baseCase`, `_consCase`) |
| 3 | Bash (ghc) | Cycle 1 compile -- collect diagnostics for both holes |
| 4 | Edit | Fill `_baseCase` with `mempty` |
| 5 | Bash (ghc) | Cycle 2 compile -- confirm `_baseCase` filled, get `_consCase` diagnostics |
| 6 | Edit | Fill `_consCase` with `f x <> myFoldMap f xs` |
| 7 | Bash (ghc) | Cycle 3 compile -- confirm success |

(Plus 1 Read to verify final file and 1 Write for this assessment = 9 total including bookkeeping.)
