# Design

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

## Decisions

- **Two extending skills, not one**: Compiler loop and reasoning loop are fundamentally different workflows. Mixing them risks bloat.
- **Three-layer architecture**: Core skill for shared philosophy enables future extension without duplication.
- **Full autonomy**: Claude runs the loop until done, stopping only on ambiguity or being stuck.
- **Compilation as success criterion**: No tests. The type checker is the oracle.
- **Visible holes**: Placeholders written to file so human sees skeleton evolve in editor.
- **Haskell first**: Most mature typed hole support. Lean 4 and Rust follow.
- **Auto-detect compiler**: Check project files (`.cabal`, etc.) to determine invocation.

## Non-Goals

- Language-specific extending skills (Haskell, Lean 4, Rust) — future work
- Test integration — out of scope; compilation is success
- IDE integration — these are Claude Code skills, not editor plugins
