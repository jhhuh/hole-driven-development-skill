# Experiment-Driven Skill Development

Three skills for developing, validating, and improving Claude Code skills through blind experimentation.

## Skills

| Skill | Purpose |
|-------|---------|
| `blind-skill-assessment` | Fair A/B comparison with randomized labels and multi-persona judging |
| `experiment-set-design` | Design task sets with baselines and phase progression |
| `iterative-skill-refinement` | The improvement loop with anti-overfitting discipline |

## How They Compose

```
experiment-set-design       — what to test, how to progress phases
├── blind-skill-assessment  — how to fairly judge results
└── iterative-skill-refinement — the improvement loop (uses both above)
```

Each skill is independently useful. The refinement skill references the other two.

## Test Results

All three skills were developed using TDD for skills (RED-GREEN-REFACTOR):

| Skill | Baseline Gaps Found | GREEN Test |
|-------|-------------------|------------|
| blind-skill-assessment | No randomization, single perspective, holistic verdicts, no rubric, no confidence | 5/5 process steps followed |
| experiment-set-design | No baseline principle, no anti-overfitting, no phase progression, no assessment variation | All 6 gaps addressed |
| iterative-skill-refinement | No structured loop, no re-experimentation, no overfitting warning, no convergence | Full 7-step loop followed |

Integration test: all three skills compose correctly on a novel scenario (defensive-error-handling skill improvement).

## Installation

```bash
cp -r skills/ your-project/.claude/skills/
# or
cp -r skills/ ~/.claude/skills/
```

## Origin

Extracted from the [HDD skill project](https://github.com/jhhuh/hole-driven-development-skill) methodology (35 experiments, 5/5 blind review wins).
