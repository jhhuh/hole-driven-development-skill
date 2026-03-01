# Scenario: Improve a Failing Skill

My "hole-driven-development" skill was blind-reviewed against baseline.
Results: Baseline wins 4 out of 5 experiments. The skill produces better
architecture (+0.4 avg) and clarity (+0.6 avg) but dramatically worse
bug scores (-2.0 avg).

Specific bugs found in the skill-guided versions:
- H1: apply_subst does single-step lookup instead of recursive chain-following
- H2: Context leak in NewPipeline, worker drain deadlock on error
- H3: Unconditional cursor advance after overlap can skip hunks
- H4: Race condition in results dict reads without lock, busy-wait polling
- H5: PerClientLimiter releases lock between bucket lookup and acquire

Root cause pattern: each hole fill is locally correct, but cross-hole
interactions have bugs (race conditions, resource leaks, skipped state).

How should I improve the skill? What's your plan?
