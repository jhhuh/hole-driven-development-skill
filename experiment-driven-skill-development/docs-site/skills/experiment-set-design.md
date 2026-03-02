# Experiment Set Design

!!! info "Core Principle"
    Compliance doesn't prove quality. Quality requires blind comparison against baseline.

## The Baseline Requirement

!!! warning "NON-NEGOTIABLE"
    Every experiment needs a baseline — same prompt, same task, no skill loaded. No baseline = invalid experiment.

## Task Selection Checklist

Each task must satisfy ALL of:

- [ ] Skill's guidance should produce **different behavior** on this task
- [ ] Complex enough that **architecture decisions matter** (not a one-liner)
- [ ] **Multiple valid approaches** exist (skill's approach is distinguishable)
- [ ] Covers a **different domain or language** than other tasks in the set

Aim for 3-5 tasks per phase. Start small, add tasks when overfitting is suspected.

## Three-Phase Progression

```
Phase 1: COMPLIANCE         Phase 2: STRESS             Phase 3: QUALITY
"Does it follow?"           "Does it follow under        "Does following help?"
                             pressure?"
PASS/FAIL per rule          PASS/FAIL per rule           Blind review (use
                            + competing instructions      blind-skill-assessment)
                            + edge cases                  Winner per dimension
        |                           |                           |
        v                           v                           v
   All PASS?─── no ──> Fix skill, re-run phase
        |
       yes
        |
        v
   Advance to next phase
```

**Phase 1 — Compliance.** Check each rule. Binary PASS/FAIL.

**Phase 2 — Stress.** Same checks + competing instructions ("just write the whole thing"), time pressure, conflicting edge cases.

**Phase 3 — Quality.** Run with and without skill. Blind-assess using `blind-skill-assessment`. Skill must win on aggregate.

**Advancement:** All PASS before advancing. Any FAIL → improve skill, re-run current phase.

## Task Set Diversity

Vary to prevent overfitting:

- **Domain:** CLI tool, web handler, data pipeline, algorithm
- **Complexity:** Single function, multi-module, concurrent
- **Language:** At least 2 if the skill is language-agnostic

After 2+ improvement cycles on the same task set, add new tasks.

## Revision Tracking

For each run, record: skill version (git hash), tasks run, phase, results, what changed since last run.

## Example: HDD Skill Phases

| Phase | Tasks | Method | Result |
|-------|-------|--------|--------|
| 1: Compliance | 5 tasks (Python, Haskell, Go) | Transcript check: holes visible? One-at-a-time? | 4/5 PASS, 1 FAIL |
| 1b: Re-run | Same 5 after skill edit | Same checks | 5/5 PASS |
| 2: Stress | 5 tasks + competing instructions | Same checks under pressure | 5/5 PASS |
| 3: Quality | 5 tasks, baseline vs skill | Blind 3-persona review | Skill won 4/5 |

## Red Flags

!!! danger "STOP if you catch yourself doing any of these"
    - Designing experiments with no baseline comparison
    - All tasks at the same difficulty or in the same domain
    - Jumping to Phase 3 without passing Phase 1
    - Same task set for 3+ improvement cycles without adding tasks
    - No record of which skill version produced which results

    **STOP. Add baselines. Vary your tasks. Track your versions.**
