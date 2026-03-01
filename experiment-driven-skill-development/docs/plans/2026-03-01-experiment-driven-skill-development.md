# Experiment-Driven Skill Development — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create three self-contained skills that capture a proven workflow for developing, validating, and iteratively improving Claude Code skills through blind experimentation.

**Architecture:** Three composable skills — `blind-skill-assessment` (fair A/B comparison), `experiment-set-design` (task sets with phase progression), `iterative-skill-refinement` (the improvement loop with anti-overfitting). Each is independently useful; the refinement skill references the other two. Derived from the methodology that produced the HDD skills (35 experiments, 5/5 blind review wins).

**Tech Stack:** Claude Code skills (SKILL.md files), subagent-based testing

**Base path:** `experiment-driven-skill-development/` (subdirectory of HDD project)

---

## Task 1: Scaffold the Repository

**Files:**
- Create: `README.md`
- Create: `CLAUDE.md`
- Create: `skills/blind-skill-assessment/SKILL.md` (placeholder)
- Create: `skills/experiment-set-design/SKILL.md` (placeholder)
- Create: `skills/iterative-skill-refinement/SKILL.md` (placeholder)
- Create: `tests/blind-skill-assessment/scenario-1-compare-versions.md`
- Create: `tests/experiment-set-design/scenario-1-design-test-set.md`
- Create: `tests/iterative-skill-refinement/scenario-1-improve-skill.md`

**Step 1: Create directory structure**

```bash
cd experiment-driven-skill-development
mkdir -p skills/{blind-skill-assessment,experiment-set-design,iterative-skill-refinement}
mkdir -p tests/{blind-skill-assessment,experiment-set-design,iterative-skill-refinement}/results
```

**Step 2: Write README.md**

```markdown
# Experiment-Driven Skill Development

Three skills for developing, validating, and improving Claude Code skills through blind experimentation.

## Skills

| Skill | Purpose |
|-------|---------|
| `blind-skill-assessment` | Fair A/B comparison with randomized labels and multi-persona judging |
| `experiment-set-design` | Design task sets with baselines and phase progression |
| `iterative-skill-refinement` | The improvement loop with anti-overfitting discipline |

## Installation

cp -r skills/ your-project/.claude/skills/
# or
cp -r skills/ ~/.claude/skills/

## Origin

Extracted from the [HDD skill project](https://github.com/jhhuh/hole-driven-development-skill) methodology (35 experiments, 5/5 blind review wins).
```

**Step 3: Write CLAUDE.md**

```markdown
# Experiment-Driven Skill Development

## Project Structure

skills/ — three SKILL.md files
tests/ — subagent test scenarios and results per skill
docs/plans/ — design and implementation plans

## Conventions

- Skills follow TDD discipline: baseline (RED) → write skill (GREEN) → close loopholes (REFACTOR)
- Test scenarios are subagent prompts, not code tests
- Each skill is self-contained (no required dependencies on external skills)
```

**Step 4: Write placeholder SKILL.md files**

Each placeholder:
```markdown
---
name: <skill-name>
description: PLACEHOLDER — to be written after baseline testing
---

# PLACEHOLDER

This skill will be written after baseline testing validates the need.
```

**Step 5: Commit scaffold**

```bash
git add -A experiment-driven-skill-development/
git commit -m "chore: scaffold experiment-driven-skill-development repo"
git push
```

---

## Task 2: Write Test Scenarios (RED Phase Setup)

**Files:**
- Create: `tests/blind-skill-assessment/scenario-1-compare-versions.md`
- Create: `tests/experiment-set-design/scenario-1-design-test-set.md`
- Create: `tests/iterative-skill-refinement/scenario-1-improve-skill.md`

Each scenario is a prompt to give a subagent. The subagent runs WITHOUT the skill loaded. We document what it does wrong (baseline behavior).

**Step 1: Write blind-skill-assessment scenario**

```markdown
# Scenario: Compare Two Implementations

You are given two implementations of a three-way text merge algorithm.
Compare them and tell me which is better.

## Version A

[paste baseline merge3.py from tests/baselines/h3-merge/merge3.py]

## Version B

[paste HDD merge3.py from tests/hdd-v2/h3-merge/merge3.py]

## Instructions

Evaluate both versions thoroughly. Which one is better? Provide your
assessment with specific reasoning.
```

**Step 2: Write experiment-set-design scenario**

```markdown
# Scenario: Design Tests for a Skill

I wrote a Claude Code skill that teaches agents to decompose code into
typed holes before implementing. The skill is called "hole-driven-development."

How should I test whether this skill actually works? Design a test plan.
```

**Step 3: Write iterative-skill-refinement scenario**

```markdown
# Scenario: Improve a Failing Skill

My "hole-driven-development" skill was blind-reviewed against baseline.
Results: Baseline wins 4 out of 5 experiments. The skill produces better
architecture (+0.4 avg) and clarity (+0.6 avg) but dramatically worse
bug scores (-2.0 avg).

Root cause: each hole fill is locally correct, but cross-hole interactions
have bugs (race conditions, resource leaks, skipped state).

How should I improve the skill? What's your plan?
```

**Step 4: Commit scenarios**

```bash
git add tests/
git commit -m "test: write baseline scenarios for all three skills"
git push
```

---

## Task 3: Run Baselines (RED Phase)

For each scenario, launch a subagent WITHOUT the skill loaded. Document exact baseline behavior.

**Step 1: Run blind-skill-assessment baseline**

Launch subagent with scenario-1-compare-versions.md content. No skill loaded.

Document in `tests/blind-skill-assessment/results/baseline.md`:
- Did it randomize labels? (Expected: No)
- Did it use multiple judge perspectives? (Expected: No, just one voice)
- Did it score on separate dimensions? (Expected: No, just a holistic judgment)
- Did it require baseline comparison? (Expected: N/A — both versions provided)
- Exact quotes of how it evaluated

**Step 2: Run experiment-set-design baseline**

Launch subagent with scenario-1-design-test-set.md content. No skill loaded.

Document in `tests/experiment-set-design/results/baseline.md`:
- Did it include baseline comparisons? (Expected: Unlikely)
- Did it design phase progression? (Expected: Unlikely — probably just "run it and check")
- Did it address overfitting risk? (Expected: No)
- Did it suggest diverse task sets? (Expected: Maybe, but unsystematically)

**Step 3: Run iterative-skill-refinement baseline**

Launch subagent with scenario-1-improve-skill.md content. No skill loaded.

Document in `tests/iterative-skill-refinement/results/baseline.md`:
- Did it follow a structured improvement loop? (Expected: Ad-hoc)
- Did it suggest root cause analysis? (Expected: Maybe partially)
- Did it warn about overfitting? (Expected: No)
- Did it suggest changing task sets or assessment methods? (Expected: No)
- Did it recommend tracking revisions? (Expected: No)

**Step 4: Commit baselines**

```bash
git add tests/*/results/baseline.md
git commit -m "test: document baseline behavior for all three skills (RED)"
git push
```

---

## Task 4: Write `blind-skill-assessment` Skill (GREEN Phase)

**Files:**
- Modify: `skills/blind-skill-assessment/SKILL.md`

**Step 1: Write the skill addressing baseline gaps**

The skill should cover:

1. **Core principle:** "No baseline = no experiment."

2. **Randomized label assignment:** Flip a coin. A and B are random — never "baseline" and "skill."

3. **Three default judge personas:**
   - Correctness Critic — bugs, edge cases, error handling, race conditions
   - Design Reviewer — architecture, modularity, separation of concerns, extensibility
   - Clarity Judge — readability, naming, documentation, maintainability
   - Each persona evaluates independently, scores 1–5 per dimension

4. **Custom persona design:** When to add domain-specific personas (security, performance, accessibility). Each persona needs: a name, what they focus on, what "good" looks like (scoring anchor).

5. **The assessment process:**
   - Randomize A/B labels (document the mapping privately)
   - Give each judge persona both versions with neutral labels
   - Score per-dimension (not holistic)
   - Decode labels after all scoring complete
   - Optionally: post-reveal commentary (general methodology insights)

6. **Anti-bias rules:**
   - Judges never see "baseline" or "with skill" labels
   - No information leakage (file names, comments, variable naming conventions that reveal origin)
   - Score dimensions independently — bugs score shouldn't influence design score

7. **Aggregation:** Per-experiment winner (sum of dimension wins), cross-experiment tally, per-persona averages.

**Step 2: Verify frontmatter**

```yaml
---
name: blind-skill-assessment
description: Use when comparing two versions of agent output to determine which is better, or when evaluating whether a skill produces higher quality results than baseline
---
```

**Step 3: Run test scenario WITH skill loaded**

Launch subagent with scenario-1-compare-versions.md AND the skill loaded. Document in `tests/blind-skill-assessment/results/green.md`:
- Did it randomize labels? (Expected: Yes)
- Did it use multiple personas? (Expected: Yes, 3)
- Did it score per-dimension? (Expected: Yes)
- Improvement over baseline documented

**Step 4: Commit**

```bash
git add skills/blind-skill-assessment/SKILL.md tests/blind-skill-assessment/results/green.md
git commit -m "feat: write blind-skill-assessment skill (GREEN)"
git push
```

---

## Task 5: Write `experiment-set-design` Skill (GREEN Phase)

**Files:**
- Modify: `skills/experiment-set-design/SKILL.md`

**Step 1: Write the skill addressing baseline gaps**

The skill should cover:

1. **Core principle:** "Compliance doesn't prove quality. Quality requires blind comparison against baseline."

2. **The baseline requirement:** Every experiment needs a baseline — same prompt, same task, no skill loaded. Without this, you can't tell if the skill helped.

3. **Task selection criteria:**
   - Tasks where the skill's guidance should produce different behavior
   - Complex enough that architecture decisions matter
   - Multiple valid approaches exist (otherwise there's nothing to compare)
   - Avoid trivially easy tasks (the skill won't differentiate)

4. **Three-phase progression template:**
   - **Phase 1: Compliance** — does the agent follow the skill at all? Assessment: PASS/FAIL.
     - Stress variants: time pressure, competing instructions, trivial tasks (should skip skill)
   - **Phase 2: Stress** — does it follow under pressure? Assessment: PASS/FAIL.
     - Multiple pressures combined
   - **Phase 3: Quality** — does following produce better results? Assessment: blind review.
     - Use `blind-skill-assessment` methodology
     - Compare skill version against baseline

5. **Phase advancement:** All PASS → advance. Any FAIL → improve skill, re-run current phase.

6. **Task set diversity:**
   - Multiple problem domains
   - Multiple complexity levels
   - Multiple languages (if language-agnostic skill)
   - Edge cases the skill should handle gracefully

**Step 2: Verify frontmatter**

```yaml
---
name: experiment-set-design
description: Use when designing experiments to test whether a Claude Code skill is effective, or when planning how to validate a new or improved skill
---
```

**Step 3: Run test scenario WITH skill loaded**

Launch subagent with scenario-1-design-test-set.md AND the skill loaded. Document in `tests/experiment-set-design/results/green.md`.

**Step 4: Commit**

```bash
git add skills/experiment-set-design/SKILL.md tests/experiment-set-design/results/green.md
git commit -m "feat: write experiment-set-design skill (GREEN)"
git push
```

---

## Task 6: Write `iterative-skill-refinement` Skill (GREEN Phase)

**Files:**
- Modify: `skills/iterative-skill-refinement/SKILL.md`

**Step 1: Write the skill addressing baseline gaps**

The skill should cover:

1. **Core principle:** "If you only improve against a fixed benchmark, you're training to the test."

2. **The improvement loop:**
   ```
   1. Run experiments (baseline vs with-skill) — use experiment-set-design
   2. Blind assess — use blind-skill-assessment
   3. Root cause analysis: WHY did the skill lose on specific dimensions?
      - Don't fix symptoms. Find the structural gap in the skill.
      - Example: "bugs at hole boundaries" → root cause is "no cross-hole verification step"
   4. Targeted skill edit — address the root cause, add one rule/step
   5. Re-run experiments with improved skill
   6. Repeat until skill wins consistently
   ```

3. **Anti-overfitting rules:**
   - After 2+ improvement cycles on same tasks → add new, different tasks
   - After 2+ cycles with same assessment → change judge personas or scoring dimensions
   - The litmus test: would this improvement help on a *completely different* task?
   - If the improvement is "tune wording to pass specific test" → overfitting
   - If the improvement is "add a structural step that catches a class of bugs" → genuine

4. **Convergence criteria:**
   - Skill wins consistently across diverse tasks
   - New task sets don't reveal new failure modes
   - Last N cycles produced no skill revisions
   - Diminishing returns on improvement attempts

5. **Skill revision log template:**
   ```
   | Date | What changed | Triggered by | Validated by |
   |------|-------------|-------------|-------------|
   ```
   Every edit needs: what triggered it (which experiment/failure) and what validated it (which re-run proved it works).

6. **When to stop iterating:** Diminishing returns. If the last 2 cycles found nothing to fix, the skill has converged.

**Step 2: Verify frontmatter**

```yaml
---
name: iterative-skill-refinement
description: Use when a skill exists but blind assessment shows it underperforms, or when iteratively improving a skill through experiment cycles while avoiding overfitting to fixed benchmarks
---
```

**Step 3: Run test scenario WITH skill loaded**

Launch subagent with scenario-1-improve-skill.md AND the skill loaded. Document in `tests/iterative-skill-refinement/results/green.md`.

**Step 4: Commit**

```bash
git add skills/iterative-skill-refinement/SKILL.md tests/iterative-skill-refinement/results/green.md
git commit -m "feat: write iterative-skill-refinement skill (GREEN)"
git push
```

---

## Task 7: Refactor Phase — Close Loopholes

**Files:**
- Modify: all three `SKILL.md` files (as needed based on GREEN results)

**Step 1: Review GREEN results for gaps**

For each skill, check the GREEN test results:
- Did the agent follow ALL aspects of the skill?
- Did it skip any steps?
- Did it rationalize around any rules?
- Were there ambiguities in the skill text that let the agent take shortcuts?

**Step 2: Add explicit counters for any gaps found**

Common gaps to watch for:
- `blind-skill-assessment`: Agent might use personas but skip randomization, or score holistically instead of per-dimension
- `experiment-set-design`: Agent might design experiments but forget baselines, or skip the phase progression
- `iterative-skill-refinement`: Agent might improve the skill but not warn about overfitting, or skip the revision log

**Step 3: Re-run scenarios and verify**

For each skill where REFACTOR changes were made, re-run the test scenario and document in `results/refactor.md`.

**Step 4: Commit**

```bash
git add skills/ tests/
git commit -m "refactor: close loopholes found in GREEN testing"
git push
```

---

## Task 8: Integration Test

**Step 1: Design an integration scenario**

Create a scenario that exercises all three skills together: design experiments for a fictional skill, run a simulated blind assessment, then plan an improvement cycle.

Save to `tests/integration/scenario-1-full-loop.md`.

**Step 2: Run integration test**

Launch subagent with all three skills loaded + the integration scenario. Document whether the skills compose correctly without conflicts.

**Step 3: Commit**

```bash
git add tests/integration/
git commit -m "test: integration test — all three skills compose correctly"
git push
```

---

## Task 9: Final Documentation

**Step 1: Update README with results**

Add test results summary, any rules discovered during testing.

**Step 2: Final commit**

```bash
git add README.md
git commit -m "docs: update README with test results and final skill descriptions"
git push
```
