# Blind Skill Assessment

!!! info "Core Principle"
    No baseline, no experiment. Every assessment compares two versions under blinded conditions with structured scoring.

## Process

```
1. BLIND     — Randomly assign labels A/B. Record mapping privately.
               Strip origin hints (filenames, "baseline"/"skill" comments).
2. RUBRIC    — State scoring dimensions before reading the code.
3. JUDGE     — Three personas score both versions (1-5 per dimension).
4. DECODE    — Reveal A/B mapping only after ALL scoring is complete.
5. AGGREGATE — Tally dimension wins, compute per-persona averages.
```

## Default Personas

| Persona | Focus | Dimensions |
|---------|-------|------------|
| **Bug Hunter** | Correctness | Bugs, edge cases, error handling, race conditions |
| **Architect** | Design | Modularity, separation of concerns, extensibility |
| **Pragmatist** | Clarity | Readability, naming, documentation, maintainability |

Each persona scores 1-5 per dimension for both A and B, then picks a per-dimension winner. Append confidence: `[h]` high, `[m]` medium, `[l]` low.

### Scoring Anchors

| Score | Meaning |
|:-----:|---------|
| **1** | Broken |
| **2** | Significant issues |
| **3** | Adequate |
| **4** | Good, minor issues |
| **5** | Excellent |

## Anti-Bias Rules

- Judges never see origin labels ("baseline", "skill-version", "v1", "v2")
- Randomize which version is A — do not always assign the first-listed input as A
- Score each dimension independently — no holistic verdicts
- Sanitize identifying information (file paths, naming conventions that leak origin)

## Custom Personas

Add a domain-specific persona when the defaults don't cover the task's concerns. Each needs:

- **Name** — role title
- **Focus area** — one sentence
- **Scoring anchors** — what 1 and 5 mean for this persona

## Aggregation

1. **Per-experiment:** Dimension wins across all personas. More wins takes the experiment.
2. **Cross-experiment:** Tally experiment wins as "X/N won by [version]."
3. **Per-persona:** Average scores to identify where improvement is strongest/weakest.

## Example

Task: Compare two implementations of `merge3()`.

```
## Label Assignment (private)
Coin flip: tails → Version A = skill-version, Version B = baseline

## Bug Hunter — Correctness
           A    B
Edge cases: 4[h] 3[h]  — A handles empty-file edge case, B does not
Error path: 3[m] 3[m]  — both miss error on binary input
Winner: A

## Architect — Design
              A    B
Modularity:    4[h] 3[h]  — A separates hunk extraction cleanly
API surface:   3[m] 4[m]  — B's top-level API has better early-exit
Winner: tie

## Pragmatist — Clarity
              A    B
Readability:   3[h] 4[h]  — B's variable names are clearer
Documentation: 4[m] 3[m]  — A has better docstring coverage
Winner: tie

## Decode
A = skill-version, B = baseline

## Result
Dimension wins: A=3, B=2, ties=1 → A wins this experiment.
```

## Red Flags

!!! danger "STOP if you catch yourself doing any of these"
    - Evaluating without randomizing labels
    - Reading origin labels before scoring is complete
    - Giving only a holistic verdict with no per-dimension scores
    - Skipping the upfront rubric ("I'll just see what stands out")
    - Using a single perspective instead of multiple personas

    **STOP. Randomize. Score per-dimension. Then proceed.**
