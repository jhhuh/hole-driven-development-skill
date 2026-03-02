# Origin Story

These skills were extracted from the methodology used to develop the [Hole Driven Development](https://jhhuh.github.io/hole-driven-development-skill/) Claude Code skills.

## The HDD Experiment Journey

The HDD skill teaches agents to decompose code into typed holes and fill them iteratively. Developing it required answering a hard question: **does the skill actually produce better code than baseline?**

### Phase 1: Compliance (24 experiments)

First, we checked whether agents follow the skill at all. 5 tasks across Python, Haskell, and Go, checking each rule (visible holes, one-at-a-time, most-constrained-first, stop when ambiguous).

Result: 4/5 PASS initially, 5/5 after a skill edit. Compliance confirmed.

### Phase 2: Stress (24 experiments)

Same tasks with competing instructions ("just write the whole thing"), time pressure, and edge cases.

Result: 5/5 PASS. The skill holds under pressure.

### Phase 3: Quality (35 experiments)

The critical test. 5 hard tasks (type inference, pipeline, 3-way merge, task scheduler, rate limiter), each run with and without the skill. Blind 3-persona review with randomized labels.

**First result: Baseline won 4/5.** The skill produced better architecture (+0.4 avg) and clarity (+0.6 avg) but dramatically worse bug scores (-2.0 avg). Each hole fill was locally correct, but cross-hole interactions had bugs.

### The Improvement Cycle

This is where the methodology that became these skills was born:

1. **Root cause analysis** — bugs were at hole boundaries (shared state, resource lifecycle, error paths)
2. **Targeted edit** — added a VERIFY step checking cross-hole interactions after each fill
3. **Anti-overfitting check** — VERIFY is structural (catches a class of bugs), not task-specific
4. **Re-run** — HDD v2 won 5/5

The improvement was genuine: a structural step that catches cross-hole interaction bugs on any codebase, not wording tuned to pass 5 specific tests.

### Key Insight

**Compliance and quality are different things.** An agent can follow every rule perfectly and still produce worse code. Only blind A/B comparison against baseline reveals whether a skill helps.

## From Methodology to Skills

The three skills capture the patterns that emerged:

| Pattern | Skill |
|---------|-------|
| Randomized labels, multi-persona judging, per-dimension scoring | [blind-skill-assessment](skills/blind-skill-assessment.md) |
| Baselines, phase progression, task diversity | [experiment-set-design](skills/experiment-set-design.md) |
| Diagnose-triage-edit-rerun loop, anti-overfitting | [iterative-skill-refinement](skills/iterative-skill-refinement.md) |

The methodology is now reusable: any Claude Code skill can be developed, validated, and improved using these three skills.
