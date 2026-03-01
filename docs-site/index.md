# Hole Driven Development — Claude Code Skills

[:material-github: View on GitHub](https://github.com/jhhuh/hole-driven-development-skill){ .md-button }

Three composable skills that teach Claude Code agents to implement code using **Hole Driven Development** (HDD), a top-down programming technique from Haskell.

## Why Use This?

Without these skills, Claude Code writes complete implementations in one pass — all logic at once, no visible decomposition, no intermediate states for you to review. You see the final code, and by then it's too late to influence the approach.

With HDD skills, the agent decomposes first, then fills one piece at a time. You watch the skeleton evolve in your editor and can intervene at any step.

!!! success "Validated across 24 experiments in 5 languages with 24/24 PASS"

| | Without skills | With HDD skills |
|---|---|---|
| **Decomposition** | Mental (invisible to you) | Written to the file as holes |
| **Implementation** | All at once, single pass | One hole per iteration |
| **Fill order** | Reading order or arbitrary | Most constrained first (fewer errors) |
| **Code structure** | Monolithic functions | Modular helpers with clear contracts |
| **Ambiguity** | Silently picks one interpretation | Stops and asks you to choose |
| **Tool calls** | 5–7 per task | 14–43 per task (more checkpoints) |

See [Skill vs Baseline](results.md) for full comparison data.

## Add to Your Workflow

Install the skills, then use them naturally in your Claude Code sessions:

- **Haskell / Lean 4 / Rust project?** The compiler loop skill kicks in when it sees typed holes (`.hs`, `.lean`, or `.rs` files).
- **Python / TypeScript / Go / Bash?** The iterative reasoning skill writes visible hole markers.
- **Trivial one-liner?** The core skill's red-flag list prevents over-decomposition.

## Skills

| Skill | What it does | Oracle |
|-------|-------------|--------|
| [`hole-driven-development-core`](skills/core.md) | Philosophy — decompose, visible holes, one at a time, most constrained first | Abstract |
| [`hole-driven-development`](skills/compiler-loop.md) | Compiler loop — compile, read diagnostics, fill, repeat | GHC / compiler |
| [`hole-driven-development-iterative-reasoning`](skills/iterative-reasoning.md) | Claude reasons about each hole's contract, writes visible markers | Claude's reasoning + optional type checker |

### Architecture

```
hole-driven-development-core          ← philosophy (always loaded)
├── hole-driven-development           ← compiler feedback loop (Haskell, Lean 4, Rust)
└── hole-driven-development-iterative-reasoning  ← reasoning loop (any language)
```

## Installation

Copy the `skills/` directory into your Claude Code skills location:

```bash
# Per-project
cp -r skills/ your-project/.claude/skills/

# Or user-wide
cp -r skills/ ~/.claude/skills/
```

## Quick Start

### Compiler Loop (Haskell)

Load `hole-driven-development`. Give Claude a type signature with a hole:

```haskell
myFoldr :: (a -> b -> b) -> b -> [a] -> b
myFoldr = _
```

Claude autonomously compiles, reads diagnostics, and fills holes one at a time until compilation succeeds.

### Compiler Loop (Lean 4)

```lean
def myAppend (xs ys : List α) : List α := sorry
```

Claude builds with `lake`, reads "unsolved goals" diagnostics, and fills `sorry` placeholders iteratively.

### Compiler Loop (Rust)

```rust
fn my_map<T, U>(xs: Vec<T>, f: impl Fn(T) -> U) -> Vec<U> {
    todo!("map")
}
```

Claude builds with `cargo`, uses intentional type mismatches to extract constraints, and fills `todo!()` placeholders iteratively.

### Iterative Reasoning (any language)

Load `hole-driven-development-iterative-reasoning`. Ask Claude to implement a function:

> Implement `parse_csv(text: str) -> list[dict[str, str]]` — handle quoted fields.

Claude writes visible hole markers, reasons about each contract, and fills one at a time.

## Supported Languages

**Compiler loop** (real typed holes):

- Haskell (GHC)
- Lean 4 (`lake` / `lean`)
- Rust (`cargo` / `rustc`)

**Iterative reasoning** (hole markers):

- Python, JavaScript/TypeScript, Go, Bash, and any other language
