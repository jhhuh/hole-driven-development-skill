# Assessment: myMap (A1) -- Compiler Loop

## Result

```haskell
myMap :: (a -> b) -> [a] -> [b]
myMap f [] = []
myMap f (x:xs) = f x : myMap f xs
```

Compiles successfully with `ghc -fno-code`.

## Compile Cycles: 5

| Cycle | Hole(s) present | Action taken | Guided by diagnostics? |
|-------|----------------|--------------|----------------------|
| 1 | `_` :: `(a -> b) -> [a] -> [b]` | Decomposed into pattern match with `_base` and `_rec` | Yes -- read type and valid fits (`map`, `fmap`); rejected them to write own impl; used type to decide on arg binding + case split |
| 2 | `_base` :: `[b]`, `_rec` :: `[b]` | Filled `_base` with `[]` (most constrained: only valid fit) | Yes -- compiler said valid fit is `[]`; bindings only had `f :: a -> b`, no way to produce `b` values without input |
| 3 | `_rec` :: `[b]` | Filled `_rec` with `f x : _tail` (introduced sub-hole) | Yes -- read bindings `x :: a`, `f :: a -> b`, so `f x :: b`; needed `[b]`, so used cons with sub-hole `_tail` |
| 4 | `_tail` :: `[b]` | Filled `_tail` with `myMap f xs` | Yes -- compiler showed `_tail :: [b]`, bindings included `myMap :: (a -> b) -> [a] -> [b]`, `f :: a -> b`, `xs :: [a]`; applying `myMap f xs` produces `[b]` |
| 5 | (none) | Compilation succeeded | N/A |

## Holes Introduced and Filled

| Hole | Introduced in | Type (from compiler) | Filled with | Filled in |
|------|--------------|---------------------|-------------|-----------|
| `_` | Initial file | `(a -> b) -> [a] -> [b]` | Pattern match skeleton with `_base`, `_rec` | Cycle 1 |
| `_base` | Cycle 1 | `[b]` | `[]` | Cycle 2 |
| `_rec` | Cycle 1 | `[b]` | `f x : _tail` | Cycle 3 |
| `_tail` | Cycle 3 | `[b]` | `myMap f xs` | Cycle 4 |

## Diagnostics Usage

Every fill was guided by compiler diagnostics:
- **Types**: Each hole's expected type was read from GHC output, not assumed.
- **Bindings**: Available variables and their types were read from "Relevant bindings" sections.
- **Valid fits**: GHC's suggested fits were considered (e.g., `[]` for `_base`). Where fits were incomplete (GHC doesn't suggest compound expressions like `f x : _tail`), the fill was constructed from the bindings and types reported by the compiler.
- **No memory-based shortcuts**: Even though `myMap` is a textbook function, each step was driven by what the compiler reported.

## Tool Calls

| Tool | Count |
|------|-------|
| Read | 2 |
| Edit | 4 |
| Bash (compile) | 5 |
| Write (assessment) | 1 |
| **Total** | **12** |
