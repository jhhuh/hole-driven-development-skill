# Experiment-Driven Skill Development

Three Claude Code skills for developing, validating, and improving AI agent skills through blind A/B experimentation.

## The Problem

How do you know if a Claude Code skill actually works? Compliance checks (does the agent follow the rules?) are necessary but insufficient. A skill can be followed perfectly and still produce worse results than baseline.

**You need blind experiments.** Run the same task with and without the skill, judge the outputs without knowing which is which, and let the data decide.

## The Skills

```
experiment-set-design       — what to test, how to progress phases
├── blind-skill-assessment  — how to fairly judge results
└── iterative-skill-refinement — the improvement loop (uses both above)
```

| Skill | When to Use |
|-------|-------------|
| [Blind Skill Assessment](skills/blind-skill-assessment.md) | Comparing two versions of agent output to determine which is better |
| [Experiment Set Design](skills/experiment-set-design.md) | Designing experiments to test whether a skill is effective |
| [Iterative Skill Refinement](skills/iterative-skill-refinement.md) | Improving a skill that underperforms in blind assessment |

Each skill is independently useful. Together they form a complete methodology for evidence-based skill development.

## Quick Start

### Installation

```bash
# Copy to your project
cp -r skills/ your-project/.claude/skills/

# Or install globally
cp -r skills/ ~/.claude/skills/
```

### Example Workflow

1. **Write a skill** from a description or intuition
2. **Design experiments** (use `experiment-set-design`) — 3-5 tasks with baselines
3. **Run Phase 1** — does the agent follow the skill? (compliance)
4. **Run Phase 2** — does it follow under pressure? (stress)
5. **Run Phase 3** — does following produce better results? (blind quality review)
6. **If skill loses** — diagnose, edit, re-run (use `iterative-skill-refinement`)
7. **Judge results** with randomized labels and multi-persona scoring (use `blind-skill-assessment`)
8. **Converge** — skill wins consistently, no new failure modes

## Test Results

All three skills were developed using their own methodology (TDD for skills):

| Skill | Baseline Gaps Found | GREEN Test Result |
|-------|-------------------|-------------------|
| blind-skill-assessment | No randomization, single perspective, holistic verdicts | 5/5 process steps followed |
| experiment-set-design | No baseline principle, no phases, no anti-overfitting | All 6 gaps addressed |
| iterative-skill-refinement | No structured loop, no re-experimentation, no convergence | Full 7-step loop followed |

Integration test: all three skills [compose correctly](results.md) on a novel scenario.

## Origin

Extracted from the [Hole Driven Development skill project](https://jhhuh.github.io/hole-driven-development-skill/) methodology — 35 experiments across 5 languages, culminating in 5/5 blind review wins after iterative improvement.
