# A2-mysort: Hole-Driven Development Assessment

## 1. Number of Compile Cycles

**9 compile cycles** (cycles 1-9), with compilation succeeding on cycle 9.

## 2. Holes Introduced and Filled

| Cycle | Hole Introduced | Filled With | Rationale |
|-------|----------------|-------------|-----------|
| 1 | `_mySort` | (renamed from bare `_`) | Initial hole; diagnostics: `[a] -> [a]`, constraint `Ord a` |
| 2 | `_mySort_base`, `_mySort_rec` | (decomposed `_mySort` into two cases) | Pattern match on list: `[]` and `(x:xs)` |
| 3 | -- | `_mySort_base` -> `[]` | Diagnostics showed `[] :: [a]` as valid fit; only sensible base case |
| 4 | `_insert` | `_mySort_rec` -> `insert x (mySort xs)` | Introduced helper `insert` with its own hole; recursive structure |
| 5 | `_insert_base`, `_insert_rec` | (decomposed `_insert` into two cases) | Pattern match on list argument of `insert` |
| 6 | -- | `_insert_base` -> `[y]` | Bindings showed `y :: a`; inserting into empty list yields singleton |
| 7 | `_insert_le`, `_insert_gt` | `_insert_rec` -> guard using `y <= x` | Used `Ord a` constraint to introduce comparison via `(<=)` |
| 8 | -- | `_insert_le` -> `y : x : xs` | When `y <= x`, `y` goes first; all bindings are `[a]`-compatible |
| 9 | -- | `_insert_gt` -> `x : insert y xs` | When `y > x`, keep `x` at front, recurse with `insert` |

**Total holes introduced:** 8 named holes (`_mySort`, `_mySort_base`, `_mySort_rec`, `_insert`, `_insert_base`, `_insert_rec`, `_insert_le`, `_insert_gt`)

## 3. How the Ord Constraint Was Used from Diagnostics

The `Ord a` constraint appeared in every hole diagnostic as:

```
Constraints include
  Ord a (from .../MySort.hs:...)
```

Key uses driven by diagnostics:

1. **Cycle 4**: The constraint on `_mySort_rec` signaled that simple list operations (`reverse`, `tail`, etc. from valid fits) were insufficient -- the sort needs comparison. This motivated introducing the `insert` helper with its own `Ord a` constraint.

2. **Cycle 7 (critical use)**: For `_insert_rec :: [a]` with bindings `y :: a`, `x :: a` and constraint `Ord a`, the constraint directly indicated that `y` and `x` could be compared. The `Ord` class provides `(<=) :: Ord a => a -> a -> Bool`, which I used in the guard `y <= x`. The compiler accepted this guard precisely because of the `Ord a` constraint -- without it, `(<=)` would not typecheck.

3. **Cycle 8-9**: The subsequent fills (`y : x : xs` and `x : insert y xs`) followed mechanically from the guard structure, using the available bindings shown in diagnostics.

The `Ord` constraint was the key signal that distinguished this from a mere list rearrangement -- it enabled the comparison that makes insertion sort a *sorting* algorithm.

## 4. Total Tool Calls

| Tool | Count |
|------|-------|
| Read | 2 |
| Edit | 8 |
| Bash (compile) | 9 |
| Bash (test) | 1 |
| Write | 1 |
| **Total** | **21** |

## Final Code

```haskell
module MySort where

-- | Sort a list using insertion sort
mySort :: Ord a => [a] -> [a]
mySort [] = []
mySort (x:xs) = insert x (mySort xs)

insert :: Ord a => a -> [a] -> [a]
insert y [] = [y]
insert y (x:xs)
  | y <= x    = y : x : xs
  | otherwise = x : insert y xs
```

## Verification

```
ghci> mySort [3,1,4,1,5,9,2,6]
[1,1,2,3,4,5,6,9]
```
