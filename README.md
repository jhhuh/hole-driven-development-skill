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

These skills were developed using TDD applied to documentation (RED-GREEN-REFACTOR) and validated through **24 systematic experiments** across 5 languages:

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

**Score: Baseline 4 · HDD 1**

| | 🔍 Bugs | 🏗️ Design | 📖 Clarity | |
|:---|:---:|:---:|:---:|:---|
| **H1: Type Inference** | | | | |
| Baseline | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | **Winner** |
| HDD | ★★☆☆☆ | ★★★★☆ | ★★★★★ | |
| **H2: Go Pipeline** | | | | |
| Baseline | ★★★★★ | ★★★★☆ | ★★★★☆ | **Winner** |
| HDD | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | |
| **H3: Three-Way Merge** | | | | |
| Baseline | ★★★★☆ | ★★★★☆ | ★★☆☆☆ | **Winner** |
| HDD | ★★☆☆☆ | ★★★☆☆ | ★★★★☆ | |
| **H4: Build System** | | | | |
| Baseline | ★★★★★ | ★★★☆☆ | ★★★★★ | **Winner** |
| HDD | ★★☆☆☆ | ★★★★☆ | ★★☆☆☆ | |
| **H5: Rate Limiter** | | | | |
| Baseline | ★★★★☆ | ★★☆☆☆ | ★★☆☆☆ | |
| HDD | ★★★☆☆ | ★★★★☆ | ★★★★★ | **Winner** |

> HDD averages higher on Design (3.6 vs 3.2) and Clarity (3.8 vs 3.2) but lower on Bugs (2.4 vs 4.4). Cleaner architecture, but iterative hole-filling introduces subtle correctness bugs. This drives the next iteration of skill prompts.

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
├── hole-driven-development                     ← compiler feedback loop (Haskell)
└── hole-driven-development-iterative-reasoning ← reasoning loop (any language)
```

## Supported Languages

**Compiler loop:** Haskell (GHC). Lean 4 and Rust planned.

**Iterative reasoning:** Python, TypeScript, Go, Bash — any language.

## License

MIT
