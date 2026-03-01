# Compiler Loop Skill

Drive implementation through the compiler's typed hole diagnostics. Write holes, compile, read what the compiler tells you, fill one hole, repeat.

**Requires:** [`hole-driven-development-core`](core.md)

## When to Use

- Source file has typed holes (`_`, `_name` in Haskell; `sorry`/`_` in Lean; `todo!()` in Rust)
- A compiler is available that reports hole diagnostics
- You're implementing against a type signature

## The Compiler Loop

```
1. Write type signature + stub with hole(s) in the file
2. COMPILE — run the compiler
3. READ diagnostics: expected type, bindings in scope, valid hole fits
4. PICK the most constrained hole (fewest valid fits)
5. FILL exactly one hole — guided by diagnostics, not memory
6. COMPILE again — go to 3
7. EXIT when compilation succeeds (no holes remain)
```

**One hole per compile cycle.** Fill one, compile, read. Do not batch-fill.

**Use named holes.** `_name` (e.g., `_base`, `_recursive`) instead of bare `_`. Easier to track across cycles.

**Diagnostics over memory.** Even if you "know" the answer, compile first.

## Compiler Invocation

| Language | Hole syntax | Compile command | Detection |
|----------|------------|-----------------|-----------|
| Haskell | `_`, `_name` | `cabal build` if `.cabal`; otherwise `ghc <file> -fno-code` | `.cabal`, `.hs` |

## Reading GHC Diagnostics

GHC's typed hole output gives you:

1. **Found hole: `_ :: <type>`** — what type the hole needs
2. **Relevant bindings** — what's in scope with types
3. **Valid hole fits** — expressions that type-check in this position

!!! warning "Misleading fits"
    GHC may suggest a value that type-checks but is semantically wrong (e.g., `z` instead of a recursive call). Cross-reference with the function's purpose.

## Example: `myFoldr`

Starting point:
```haskell
myFoldr :: (a -> b -> b) -> b -> [a] -> b
myFoldr = _
```

**Cycle 1:** Compile → `_ :: (a -> b -> b) -> b -> [a] -> b`. Introduce pattern matching:
```haskell
myFoldr f z []     = _empty
myFoldr f z (x:xs) = _cons
```

**Cycle 2:** `_empty :: b` (fits: `z`) and `_cons :: b`. Most constrained: `_empty`. Fill with `z`.

**Cycle 3:** `_cons :: b`, bindings: `f :: a -> b -> b`, `x :: a`, `xs :: [a]`. Decompose: `f x _rest`.

**Cycle 4:** `_rest :: b`, bindings include `myFoldr`. Fill with `myFoldr f z xs`.

**Cycle 5:** Compilation succeeds.

```haskell
myFoldr f z []     = z
myFoldr f z (x:xs) = f x (myFoldr f z xs)
```
