# Experiment-Driven Skill Development

## Project Structure

skills/ — three SKILL.md files
tests/ — subagent test scenarios and results per skill
docs/plans/ — design and implementation plans

## Conventions

- Skills follow TDD discipline: baseline (RED) -> write skill (GREEN) -> close loopholes (REFACTOR)
- Test scenarios are subagent prompts, not code tests
- Each skill is self-contained (no required dependencies on external skills)
