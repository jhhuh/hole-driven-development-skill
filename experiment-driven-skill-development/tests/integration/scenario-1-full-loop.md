# Scenario: Full Experiment-Driven Skill Development Loop

You are developing a Claude Code skill called "defensive-error-handling" that
teaches agents to handle errors defensively (check return values, validate
inputs at boundaries, use structured error types).

You have written a first draft of the skill. An initial blind assessment
against baseline shows mixed results:

## Assessment Data

5 experiments, 3 judge personas (Bug Hunter, Architect, Pragmatist):

| Exp | Baseline Bug | Skill Bug | Baseline Arch | Skill Arch | Baseline Prag | Skill Prag |
|-----|:-----------:|:---------:|:------------:|:----------:|:-------------:|:----------:|
| E1  | 3           | 4         | 3            | 4          | 3             | 3          |
| E2  | 4           | 3         | 3            | 4          | 3             | 4          |
| E3  | 3           | 4         | 2            | 4          | 3             | 4          |
| E4  | 4           | 2         | 3            | 3          | 4             | 3          |
| E5  | 3           | 3         | 3            | 4          | 3             | 4          |

Winners: Skill wins E1, E3, E5 (3/5). Baseline wins E2, E4 (2/5).

Bug analysis for E2 and E4 (where skill lost):
- E2: Skill version wraps every function call in try/catch, making error flows
  hard to trace. Excessive defensiveness obscures the happy path.
- E4: Skill version validates inputs redundantly — the same value is checked
  at three layers, violating DRY.

## Your Tasks

Using the experiment-driven skill development methodology:

1. Diagnose why the skill lost on E2 and E4 (root cause, not symptoms)
2. Plan a targeted skill edit to address the root cause
3. Plan re-experimentation to validate the edit
4. Check for overfitting risk
5. Define convergence criteria for this skill

Use all three skills: experiment-set-design for the re-experimentation plan,
blind-skill-assessment for how to judge results, and iterative-skill-refinement
for the improvement loop structure.
