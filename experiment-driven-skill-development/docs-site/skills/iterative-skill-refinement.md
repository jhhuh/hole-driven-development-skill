# Iterative Skill Refinement

!!! info "Core Principle"
    If you only improve against a fixed benchmark, you're training to the test. Every improvement must generalize beyond the tasks that revealed it.

## The Improvement Loop

```
1. EXPERIMENT — Run baseline vs skill on diverse tasks
2. ASSESS    — Blind assess (use blind-skill-assessment)
   └─ Skill wins consistently? → DONE (see Convergence)
3. DIAGNOSE  — Root cause on dimensions where skill lost
   └─ Don't fix symptoms. Ask: "What class of bugs does this represent?"
   └─ Example: "bugs at hole boundaries" → missing cross-hole verification
4. TRIAGE    — Rank causes by breadth. Fix the widest-impact cause first.
5. EDIT      — One targeted change for one root cause. Log it (see Revision Log).
6. RE-RUN    — New experiments with improved skill
   └─ 2+ cycles on same tasks? Add new tasks (see Anti-Overfitting)
   └─ 2+ cycles with same judges? Rotate personas or dimensions
7. GOTO 2
```

## Anti-Overfitting Checklist

Before committing any skill edit, answer all four:

| Check | Pass | Fail |
|-------|------|------|
| Would this help on a completely different task? | Structural improvement | Overfitting |
| Does this add a general step/rule, not task-specific wording? | Genuine | Overfitting |
| After 2+ cycles on same tasks, did you add new tasks? | Fresh signal | Stale benchmark |
| After 2+ cycles with same judges, did you rotate personas? | Diverse signal | Judge-fitted |

!!! tip "Litmus Test"
    "Adds a structural step catching a class of bugs" = genuine. "Tunes wording to pass a specific test" = overfitting.

## Convergence — When to Stop

Stop when **all** hold:

1. Skill wins consistently across diverse tasks (not just original set)
2. New task sets reveal no new failure modes
3. Last 2 cycles produced no revisions
4. Gains per cycle are diminishing

## Revision Log

Every skill edit gets a row. No undocumented changes.

| Date | What changed | Triggered by | Validated by |
|------|-------------|-------------|-------------|
| *example* | Added VERIFY step | Phase 3: bugs at hole seams | Phase 3b: HDD won 5/5 |

## Example: HDD VERIFY Step

Blind assessment: baseline won 4/5. Bug Hunter found bugs at hole boundaries — shared state and error paths crossing seams. Root cause: no cross-hole verification step. Edit: added VERIFY step (check state, scopes, error paths after each fill). Re-run: HDD won 5/5. New tasks confirmed. Converged.

## Red Flags

!!! danger "STOP if you catch yourself doing any of these"
    - Proposing fixes without a re-experimentation plan
    - Treating all failures with equal weight (no triage)
    - Editing the skill without logging what triggered and validated it
    - Same tasks for 3+ cycles without adding new ones
    - Framing success as "fewer bugs" instead of "beats baseline"
    - No convergence criteria defined before starting

    **STOP. Diagnose root cause. Plan validation. Then edit.**
