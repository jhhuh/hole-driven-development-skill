# Hole Driven Development Skills

## Project Structure

Three-layer skill hierarchy:
- `skills/hole-driven-development-core/` — HDD philosophy and abstract loop
- `skills/hole-driven-development/` — Compiler-feedback loop (Haskell first)
- `skills/hole-driven-development-iterative-reasoning/` — Claude-as-type-checker

## Dev Environment

`nix develop` provides ghc and cabal for testing the compiler-loop skill.

## Conventions

- Skills follow the writing-skills TDD discipline: RED → GREEN → REFACTOR
- Skill files are in `skills/<name>/SKILL.md`
- Test scenarios for skills go in `tests/<skill-name>/`
