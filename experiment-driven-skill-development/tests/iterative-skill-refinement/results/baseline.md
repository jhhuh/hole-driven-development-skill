# Baseline: Iterative Skill Refinement (No Skill Loaded)

## Scenario
Given Phase 3 results (Baseline wins 4/5, HDD loses on bugs), specific bug
list, and root cause pattern. Asked: "How should I improve the skill?"

## Observed Behavior

### What the agent did well
- Precise root cause analysis — traced each bug to cross-hole interactions
- Created a table mapping each bug to specific holes and emergent property
- Proposed three concrete, targeted changes (not vague suggestions)
- Explicitly stated what NOT to change (avoiding scope creep)
- Each proposed change included rationale tied to specific bugs
- Provided a summary table of exact files and changes

### What the agent did NOT do (skill gaps)

1. **No structured improvement loop.** Agent jumped straight to proposing
   fixes. No mention of: run baseline -> measure -> change skill -> re-run
   -> compare. The improvement process itself has no structure. Without a
   loop, there's no way to verify the changes actually helped.

2. **No re-experimentation plan.** Agent proposed skill changes but didn't
   say "after making these changes, re-run the experiments to verify
   improvement." The fixes are hypotheses — they need validation.

3. **No overfitting warning.** The proposed fixes are tightly targeted at
   the 5 specific bugs found. No mention of the risk that these fixes might
   only help with these specific tasks and not generalize. No suggestion to
   test on new/different tasks after fixing.

4. **No revision tracking.** Agent didn't suggest documenting what was
   changed, why, and what the before/after results were. Without a revision
   log, the improvement history is lost.

5. **No severity/priority triage.** Agent proposed three changes with equal
   weight. No guidance on which to try first, or whether to apply one change
   at a time (to measure individual impact) vs. all at once.

6. **No baseline comparison framing.** Agent analyzed the data but didn't
   frame the improvement in terms of "baseline vs. skill" comparison. The
   question is not "did bugs decrease?" but "did the skill-guided version
   beat the baseline?" Without this framing, you might improve the skill
   but still lose to baseline.

7. **No convergence criteria.** No definition of "done improving." When
   should you stop the loop? Agent didn't suggest criteria like "skill
   wins N/N experiments" or "no new bug categories for 2 iterations."

## Key Rationalizations
- None observed under pressure. The agent gave a thorough technical
  analysis. The gaps are structural — the agent knows how to diagnose
  and propose fixes, but doesn't think about the meta-process of
  iterative improvement.

## Summary of Gaps for Skill to Address

| Gap | Priority | Why it matters |
|-----|----------|---------------|
| Structured improvement loop | High | Without loop structure, improvements are ad-hoc guesses |
| Re-experimentation plan | High | Fixes are hypotheses that need validation |
| Overfitting warning | High | Targeted fixes risk over-specialization |
| Baseline comparison framing | High | Absolute improvement != winning vs. baseline |
| Convergence criteria | Medium | Need to know when to stop iterating |
| Severity triage | Medium | Apply changes incrementally to measure impact |
| Revision tracking | Medium | Can't learn from improvement history without logs |
