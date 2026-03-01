---
name: hole-driven-development
description: Use when implementing in a language with typed holes (Haskell, Lean 4, Rust) where a compiler provides hole diagnostics — runs the compiler loop autonomously
---

# Hole Driven Development — Compiler Loop

**REQUIRED BACKGROUND:** `hole-driven-development-core`

## Overview

Drive implementation through the compiler's typed hole diagnostics. Write holes, compile, read what the compiler tells you, fill one hole, repeat until it compiles.

**Core principle:** The compiler is the oracle. Every fill decision is grounded in diagnostics, not memory.

## When to Use

- Source file has typed holes (`_`, `_name` in Haskell; `sorry` / `_` in Lean; `todo!()` in Rust)
- A compiler is available that reports hole diagnostics
- You're implementing against a type signature

## The Compiler Loop

```
1. Write type signature + stub with hole(s) in the file
2. COMPILE — run the compiler
3. READ diagnostics: expected type, bindings in scope, valid hole fits
4. PICK the most constrained hole (fewest valid fits)
5. FILL exactly one hole — guided by diagnostics, not memory
   - If the fill is complex, introduce sub-holes
6. COMPILE again — go to 3
7. EXIT when compilation succeeds (no holes remain)
```

**One hole per compile cycle.** Fill one, compile, read. Do not batch-fill.

**Use named holes.** When introducing multiple holes, use `_name` (e.g., `_base`, `_recursive`) instead of bare `_`. This makes diagnostics easier to read and holes easier to track across compile cycles.

**Diagnostics over memory.** Even if you "know" the answer, compile first and let the diagnostics confirm or correct you. The compiler may reveal constraints you missed.

## Compiler Invocation

Auto-detect from project structure:

| Language | Hole syntax | Compile command | Detection |
|----------|------------|-----------------|-----------|
| Haskell | `_`, `_name` | `cabal build` if `.cabal` file exists; otherwise `ghc <file> -fno-code` | `.cabal`, `.hs` |

When using `nix develop`, prefix commands: `nix develop -c ghc ...`

## Autonomy

Run the loop autonomously. **Stop only when:**

- **Done:** Compilation succeeds — no holes remain.
- **Ambiguous:** Multiple equally valid hole fits and no constraint distinguishes them. Surface the options to the human.
- **Stuck:** 5+ compile cycles on the same hole without progress. Ask for help.

## Reading Diagnostics

GHC's typed hole output gives you:

1. **Found hole: `_ :: <type>`** — what type the hole needs
2. **Relevant bindings** — what's in scope with types
3. **Valid hole fits** — expressions that type-check in this position

**Use all three.** Valid fits narrow the search. Relevant bindings show what you can compose. The expected type is the constraint.

**Beware misleading fits.** GHC may suggest a value that type-checks but is semantically wrong (e.g., `z` instead of a recursive call). Cross-reference with the function's purpose.

## Red Flags — STOP

- Writing implementation without compiling first
- Ignoring compiler diagnostics ("I know the answer")
- Filling multiple holes between compile cycles
- Skipping compilation after a fill ("it's obviously correct")
- Looping on the same hole without trying a different approach

**If you catch yourself doing any of these: STOP. Compile. Read. Then proceed.**
