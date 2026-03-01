# Hole Driven Development Skills — Design

**Date:** 2026-03-01

## Goal

Create Claude Code skills that enable Hole Driven Development (HDD) — a top-down, type-guided programming technique originating from Haskell's typed holes. Two usage modes, three skills.

## Architecture

Three-layer, extensible:

```
hole-driven-development-core              (philosophy + decomposition)
├── hole-driven-development               (compiler-feedback loop)
│   ├── ...-haskell                       (future)
│   ├── ...-lean4                         (future)
│   └── ...-rust                          (future)
└── hole-driven-development-iterative-reasoning  (Claude-as-type-checker)
```

## Skill 1: `hole-driven-development-core`

Defines the universal HDD philosophy:

- **What HDD is**: Top-down decomposition. Start with intention, write outermost structure, leave holes, fill iteratively until none remain.
- **Abstract loop**: Receive intention → write skeleton with holes → pick most constrained hole → determine what it needs → fill (possibly introducing sub-holes) → repeat until done.
- **Hole-filling strategy**: Most constrained first. When ambiguous, stop and ask.
- **Success criterion**: No holes remain, code satisfies intention.
- **Does NOT cover**: How to determine what a hole needs (extending skill's job), language-specific syntax.

~150 words. Stable, rarely changes.

## Skill 2: `hole-driven-development`

Compiler-feedback loop for languages with real typed holes.

- **Extends**: `hole-driven-development-core`
- **Trigger**: Working in language with typed holes (Haskell, Lean 4, Rust).
- **Loop**: Write type signature + stub with holes → run compiler → parse hole diagnostics (expected type, bindings in scope, valid hole fits) → fill most constrained hole → repeat until compilation succeeds.
- **Autonomy**: Full. Stops when: compiled successfully, ambiguity with multiple equally valid fills, or stuck (5+ iterations same hole).
- **Compiler detection**: Auto-detect from project files. Initially Haskell only (`cabal build` if `.cabal` exists, `ghc` otherwise).
- **Success criterion**: Code compiles. No tests required.

Language support rollout: Haskell → Lean 4 → Rust, each as extending skills.

| Language | Hole syntax | Compiler | Detection |
|----------|------------|----------|-----------|
| Haskell  | `_`, `_name` | `cabal build` / `ghc` | `.cabal`, `.hs` |

~200 words.

## Skill 3: `hole-driven-development-iterative-reasoning`

Claude-as-type-checker for any language.

- **Extends**: `hole-driven-development-core`
- **Trigger**: Working in any language, especially without typed holes. HDD discipline for dynamically typed languages.
- **Hole markers**: Visible placeholders in the file using language-appropriate syntax (e.g., `raise NotImplementedError("HOLE_1: ...")` in Python, `throw new Error("HOLE_1: ...")` in JS/TS). Format: `HOLE_N: <description> # expects: <type/contract>`.
- **Loop**: Write skeleton with HOLE markers → pick most constrained hole → reason about what it needs (input types, output type, bindings, constraints) → fill → optionally validate with external type checker → repeat until no holes remain.
- **External tooling** (optional validation):

| Language   | Type checker      | Detection          |
|------------|------------------|--------------------|
| Python     | `mypy`, `pyright` | `pyproject.toml`   |
| TypeScript | `tsc --noEmit`    | `tsconfig.json`    |
| Go         | `go build`        | `go.mod`           |

- **Fallback**: Claude's reasoning is sole oracle when no type checker available.
- **Autonomy**: Full. Same stop conditions as compiler loop.

~250 words.

## Decisions

- **Two skills, not one**: Compiler loop and reasoning loop are fundamentally different workflows. Mixing them in one skill risks bloat.
- **Three-layer architecture**: Core skill for shared philosophy enables future extension without duplication.
- **Full autonomy**: Claude runs the loop until done, stopping only on ambiguity or being stuck. Matches HDD spirit — type checker guides, not the human.
- **Compilation as success criterion**: No tests. The type checker is the oracle.
- **Visible holes for iterative-reasoning**: Placeholders written to file so human sees skeleton evolve in editor.
- **Haskell first**: Most mature typed hole support. Lean 4 and Rust follow as extending skills.
- **Auto-detect compiler**: Check project files (`.cabal`, `stack.yaml`, etc.) to determine invocation.

## Non-Goals

- Language-specific extending skills (Haskell, Lean 4, Rust) — future work.
- Test integration — out of scope; compilation is success.
- IDE integration — these are Claude Code skills, not editor plugins.
