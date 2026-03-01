# Baseline: Experiment Set Design (No Skill Loaded)

## Scenario
Asked to design a test plan for the HDD skill (4 rules: visible decomposition,
one-at-a-time filling, most-constrained-first, stop when ambiguous).

## Observed Behavior

### What the agent did well
- Mapped each rule to a testable behavioral property
- Created a test matrix (4 properties x 3 difficulty tiers = 12 tests)
- Proposed contrastive testing (with-skill vs. without-skill)
- Suggested sample sizes and statistical methods (chi-squared/Fisher's exact)
- Proposed automated signal extraction script
- Included edge cases for later expansion (multi-file, time pressure)
- Clear measurement protocol per test

### What the agent did NOT do (skill gaps)

1. **No explicit baseline requirement stated as principle.** Agent designed
   contrastive tests (with vs. without skill) which implicitly includes
   baselines, but never stated "every experiment needs a baseline" as a
   governing principle. This matters because in practice, people skip
   baselines when rushed. The design should make baselines non-negotiable.

2. **No anti-overfitting guidance.** All 12 tests are designed upfront and
   fixed. No mention of rotating tasks, varying assessment methods, or
   watching for skills that only work on the test set. A real experiment
   loop needs mechanisms to detect and prevent overfitting.

3. **No phase progression.** All tests are at the same level — behavioral
   compliance. No progression from "does the agent follow the rules at all?"
   (compliance) to "does it follow under pressure?" (stress) to "does the
   output quality improve?" (quality/blind review). Different phases answer
   different questions about skill effectiveness.

4. **No assessment method variation.** Every test uses the same measurement
   approach (transcript analysis for behavioral signals). If the skill gets
   tuned to pass transcript-based checks, bugs might still hide in output
   quality. Varying assessment methods (transcript analysis, blind code review,
   automated testing) prevents this.

5. **No revision tracking.** No mention of logging which skill version was
   tested, what changes were made between versions, or how to compare results
   across iterations. Without this, you can't tell if your changes helped.

6. **Sample sizes are impractical.** 72-120 total runs is thorough but likely
   too expensive for iterative skill development. No guidance on starting
   with smaller sets and scaling up.

## Key Rationalizations
- None observed — the agent produced a thorough design. The gaps are about
  what the agent doesn't think to include, not what it skips under pressure.

## Summary of Gaps for Skill to Address

| Gap | Priority | Why it matters |
|-----|----------|---------------|
| Baseline as governing principle | High | Baselines get skipped in practice without explicit mandate |
| Anti-overfitting mechanisms | High | Fixed test sets lead to skill over-specialization |
| Phase progression | High | Different phases answer different effectiveness questions |
| Assessment method variation | Medium | Single method creates blind spots |
| Revision tracking | Medium | Can't measure improvement without version history |
| Practical sample sizes | Low | Guidance on scaling effort to iteration stage |
