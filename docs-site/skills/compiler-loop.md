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
6. VERIFY semantic correctness against previously filled holes:
   - Does shared state flow correctly between this fill and prior fills?
   - Are resource scopes (locks, handles, channels) consistent?
   - Do error paths compose correctly?
   The compiler catches type errors but not logic bugs.
7. COMPILE again — go to 3
8. When compilation succeeds (no holes remain):
   REVIEW-ALL — re-read the complete implementation holistically:
   - State transitions that span multiple fills
   - Resource acquired in one fill, released in another
   - Error paths that cross fill boundaries
   - Loop invariants depending on multiple fills
   Fix any systemic bug the per-hole VERIFY could not catch.
9. EXIT
```

**One hole per compile cycle.** Fill one, compile, read. Do not batch-fill.

**Use named holes.** In Haskell: `_name` (e.g., `_base`, `_recursive`) instead of bare `_`. In Lean 4: `sorry` with preceding comment or `let _base := sorry`. In Rust: `todo!("hole_name")`. Easier to track across cycles.

**Diagnostics over memory.** Even if you "know" the answer, compile first.

**When NOT to decompose further.** Some algorithms are inherently monolithic — dual-cursor walks, complex FSMs, coroutine-style loops. If the state machine's transitions are tightly coupled, keep it as one hole with internal structure via comments. The compiler catches type errors at hole boundaries but not logic bugs from split state.

## Compiler Invocation

| Language | Hole syntax | Compile command | Detection |
|----------|------------|-----------------|-----------|
| Haskell | `_`, `_name` | `cabal build` if `.cabal`; otherwise `ghc <file> -fno-code` | `.cabal`, `.hs` |
| Lean 4 | `sorry`, `_` | `lake build` if `lakefile.lean`/`lakefile.toml`; otherwise `lean <file>` | `lakefile.lean`, `.lean` |
| Rust | `todo!()` | `cargo build` if `Cargo.toml`; otherwise `rustc <file>` | `Cargo.toml`, `.rs` |

## Reading Diagnostics

### GHC (Haskell)

GHC's typed hole output gives you:

1. **Found hole: `_ :: <type>`** — what type the hole needs
2. **Relevant bindings** — what's in scope with types
3. **Valid hole fits** — expressions that type-check in this position

!!! warning "Misleading fits"
    GHC may suggest a value that type-checks but is semantically wrong (e.g., `z` instead of a recursive call). Cross-reference with the function's purpose.

### Lean 4

Lean 4's `sorry` and `_` output gives you:

1. **Unsolved goals** — the expected type for each `sorry` or `_`
2. **Context** — hypotheses available in scope with their types
3. **Expected type** — the target type the hole must produce

!!! tip "`sorry` vs `_`"
    `sorry` silences the error and allows compilation to continue — useful for incremental HDD. `_` forces the elaborator to infer and report what's needed. Prefer `sorry` for skeleton stubs.

### Rust

Rust's `todo!()` compiles successfully (it satisfies any return type via `!`), so diagnostics come from type mismatches, not the hole itself.

1. **Replace `todo!()` with `()`** to force "expected X, found ()" errors
2. **Read "expected ... found ..." messages** for the hole's required type
3. **Check "help" suggestions** for methods, traits, or conversions

!!! warning "No direct hole fits"
    Unlike GHC, Rust won't show "valid hole fits" since `todo!()` has type `!`. Rely on surrounding type context and intentional type mismatches to extract constraints.

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

## Example: `myAppend` (Lean 4)

Starting point:
```lean
def myAppend (xs ys : List α) : List α := sorry
```

**Cycle 1:** Build → unsolved goal: `List α`. Introduce pattern matching:
```lean
def myAppend : List α → List α → List α
  | [], ys => sorry  -- HOLE: base
  | x :: xs, ys => sorry  -- HOLE: cons
```

**Cycle 2:** Base case: goal is `List α`, context has `ys : List α`. Fill with `ys`.

**Cycle 3:** Cons case: goal is `List α`, context has `x : α`, `xs : List α`, `ys : List α`. Fill with `x :: myAppend xs ys`.

**Cycle 4:** Build succeeds.

## Example: `my_map` (Rust)

Starting point:
```rust
fn my_map<T, U>(xs: Vec<T>, f: impl Fn(T) -> U) -> Vec<U> {
    todo!("map")
}
```

**Cycle 1:** Replace `todo!("map")` with `()` → error: "expected `Vec<U>`, found `()`". Introduce structure:
```rust
let mut result = Vec::new();
todo!("iterate and return")
```

**Cycle 2:** Fill the loop + return:
```rust
for x in xs {
    result.push(f(x));
}
result
```

**Cycle 3:** `cargo build` succeeds.
