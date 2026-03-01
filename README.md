# Hole Driven Development — Claude Code Skills

**Claude Code skills that make agents decompose before implementing.**

Without these skills, Claude writes everything in one pass — you see the final code with no chance to influence the approach. With HDD, the agent writes a skeleton with **holes** first, fills them one at a time (most constrained first), and you watch it evolve in your editor.

## Why It Works

HDD comes from Haskell's typed holes — a technique where you leave `_` placeholders and let the compiler tell you what fits. These skills bring that discipline to Claude Code:

- **Visible decomposition.** Holes live in the file, not the agent's head. You see intermediate states.
- **One hole per iteration.** Each fill is a checkpoint — the agent re-reads, reassesses, reasons.
- **Most constrained first.** Filling the narrowest hole first narrows everything downstream.
- **Ambiguity detection.** When multiple valid approaches exist, the agent stops and asks instead of silently picking one.

## Proven Effective

These skills were developed using TDD applied to documentation (RED-GREEN-REFACTOR) and validated through **35 systematic experiments** across 5 languages:

| | Without skills | With HDD skills |
|---|---|---|
| Decomposition | Mental (invisible) | Written to file |
| Implementation | All at once | One hole per iteration |
| Code structure | Monolithic | Modular with contracts |
| Ambiguity | Silently picks one | Stops and asks |

**24/24 experiments PASS. Zero skill revisions needed after Phase 1.**

Tested scenarios range from trivial polymorphic functions to a 15-hole multi-file REST API, a type checker implementation, concurrent Go fanout, and bash backup rotation with no type system at all. Both ambiguity tests correctly triggered stop-and-ask behavior.

## Blind Code Review (Phase 3)

Five 200+ line algorithms, blind-reviewed by three AI judge personas.
Labels randomized — judges didn't know which version used HDD.

### Round 1 — Score: Baseline 4 · HDD 1

HDD averaged higher on Design (3.6 vs 3.2) and Clarity (3.8 vs 3.2) but dramatically lower on Bugs (2.4 vs 4.4). Root cause: each hole fill was locally correct, but cross-hole interactions had bugs (race conditions, resource leaks, skipped state).

### Round 2 (after VERIFY step + monolithic algorithm guidance) — Score: HDD 5 · Baseline 0

| Task | Version | 🔍 Bugs | 🏗️ Design | 📖 Clarity | |
|:---|:---|:---:|:---:|:---:|:---|
| Type Inference | Baseline | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | |
| | HDD v2 | ★★★★☆ | ★★★★☆ | ★★★★★ | **Winner** |
| Go Pipeline | Baseline | ★★★☆☆ | ★★★★☆ | ★★★★☆ | |
| | HDD v2 | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | **Winner** |
| Three-Way Merge | Baseline | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | |
| | HDD v2 | ★★★★☆ | ★★★★★ | ★★★★★ | **Winner** |
| Build System | Baseline | ★★★★☆ | ★★★☆☆ | ★★★★☆ | |
| | HDD v2 | ★★★☆☆ | ★★★★☆ | ★★★★☆ | **Winner** |
| Rate Limiter | Baseline | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ | |
| | HDD v2 | ★★★☆☆ | ★★★★☆ | ★★★★☆ | **Winner** |

| Persona | Baseline avg | HDD v2 avg | Change from v1 |
|---|:---:|:---:|:---:|
| 🔍 Bug Hunter | 3.0 | **3.6** | 2.4 → 3.6 (+1.2) |
| 🏗️ Architect | 3.0 | **4.0** | 3.6 → 4.0 (+0.4) |
| 📖 Pragmatist | 3.2 | **4.2** | 3.8 → 4.2 (+0.4) |

> Adding a VERIFY step (check shared state, resource lifecycle, and error paths) and monolithic algorithm guidance (don't decompose tightly-coupled state machines) raised Bug Hunter from 2.4 → 3.6 and flipped wins from 1/5 → 5/5.

After revealing labels, the judges commented:

*"The VERIFY step targeting shared state and resource lifecycle shows disciplined thinking about the failure modes that actually matter in production. Where it falls short is that the technique is only as good as the holes it chooses to leave: if the decomposition misses a subtle interaction between two filled holes, the per-hole verification passes cleanly while the systemic bug hides in the composition."* — Bug Hunter

*"The HDD approach enforces a discipline that naturally surfaces interface contracts before implementation details, which tends to produce cleaner separation of concerns — the skeleton phase acts as an informal API design review. Where it falls short is that the hole-filling order can lock in structural decisions early that a more exploratory pass might have revised."* — Architect

*"The HDD approach consistently produced code where the intent was legible before the implementation was complete — the skeleton communicated design decisions that a single-pass implementation buries in details. My main reservation is that the methodology adds ceremony that may not pay off for truly simple problems."* — Pragmatist

Full results: **[jhhuh.github.io/hole-driven-development-skill](https://jhhuh.github.io/hole-driven-development-skill/)**

## Installation

```bash
# Per-project
cp -r skills/ your-project/.claude/skills/

# Or user-wide
cp -r skills/ ~/.claude/skills/
```

Three composable skills:

```
hole-driven-development-core                    ← philosophy (always loaded)
├── hole-driven-development                     ← compiler feedback loop (Haskell, Lean 4, Rust)
└── hole-driven-development-iterative-reasoning ← reasoning loop (any language)
```

## Supported Languages

**Compiler loop:** Haskell (GHC), Lean 4 (`lake`/`lean`), Rust (`cargo`/`rustc`).

**Iterative reasoning:** Python, TypeScript, Go, Bash — any language.

## License

MIT
