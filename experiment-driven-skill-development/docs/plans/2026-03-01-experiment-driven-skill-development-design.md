# Design: Experiment-Driven Skill Development

## Goal

Three self-contained skills that capture the workflow for developing, validating, and iteratively improving Claude Code skills through blind experimentation. Extracted from the HDD skill project's methodology.

## Architecture

```
experiment-set-design              ← what to test, how to progress phases
├── blind-skill-assessment         ← how to fairly judge results
└── iterative-skill-refinement     ← the improvement loop (uses both above)
```

All three are independently useful. The refinement skill references the other two.

## Skill 1: `blind-skill-assessment`

**Trigger:** Use when comparing two versions of agent output to determine which is better.

**Core principle:** Every assessment compares against a baseline. No baseline = no experiment.

### Content

1. **Randomized label assignment** — flip a coin: A=baseline or A=skill-version. Never let the judge see which is which.

2. **Three default judge personas:**
   - Correctness Critic — bugs, edge cases, error handling
   - Design Reviewer — architecture, modularity, separation of concerns
   - Clarity Judge — readability, maintainability, naming
   - How to create domain-specific personas (Security Auditor, Performance Analyst, etc.)

3. **Scoring:** 1–5 per dimension, winner per experiment, aggregate averages across experiments.

4. **Label reveal:** After scoring, decode the mapping. Optionally ask judges for post-reveal commentary (general methodology insights, not task-specific).

5. **The baseline requirement:** Every assessment needs a baseline comparison. Evaluating in isolation is meaningless — you can't tell if the skill helped.

### Format

- Subagent prompt template for launching a blind judge
- Scoring rubric (what 1–5 means per dimension)
- Decode table template
- Example from HDD project (abbreviated)

## Skill 2: `experiment-set-design`

**Trigger:** Use when designing experiments to test whether a skill is effective.

**Core principle:** Compliance doesn't prove quality. Quality requires blind comparison against baseline.

### Content

1. **The baseline requirement** (reinforced): Same prompt, same task, no skill loaded. If you don't have this, your experiment proves nothing.

2. **Task selection criteria:**
   - Tasks where the skill's guidance should matter (not trivial one-liners)
   - Tasks with multiple valid approaches (so the skill's approach can be distinguished)
   - Tasks complex enough that architecture decisions affect quality

3. **Three-phase progression template:**
   - **Phase 1: Compliance** — does the agent follow the skill at all? (PASS/FAIL)
   - **Phase 2: Stress** — does it follow under pressure? (competing instructions, time pressure, edge cases)
   - **Phase 3: Quality** — does following produce better results? (blind review via `blind-skill-assessment`)

4. **Phase advancement:** All PASS in current phase → advance. Any FAIL → improve skill, re-run current phase.

5. **Task set diversity:** Multiple languages/domains/complexity levels to avoid overfitting to one scenario.

### Format

- Task design checklist
- Phase progression flowchart
- Baseline design template
- Example phase progression from HDD project (Phases 1–3)

## Skill 3: `iterative-skill-refinement`

**Trigger:** Use when a skill exists but blind assessment shows it underperforms or has weaknesses.

**Core principle:** If you only improve against a fixed benchmark, you're training to the test.

### Content

1. **The improvement loop:**
   ```
   1. Run experiments (baseline vs with-skill)
   2. Blind assess (using blind-skill-assessment)
   3. Root cause analysis — WHY did the skill lose on specific dimensions?
   4. Targeted skill edit — address the specific root cause, not symptoms
   5. Re-run experiments
   6. Repeat until skill wins consistently
   ```

2. **Anti-overfitting rules:**
   - After 2+ improvement cycles on the same task set → add new tasks
   - After 2+ cycles with the same assessment method → add/change judge personas or scoring dimensions
   - The litmus test: would this improvement help on a completely different task? If not, you're overfitting
   - Vary BOTH the independent variable (tasks) AND the measurement instrument (assessment method)

3. **Convergence criteria:**
   - Skill wins consistently across diverse tasks
   - New task sets don't reveal new failure modes
   - Skill revision log shows diminishing changes

4. **Skill revision log:** Track what changed, what triggered the change, which experiment validated it.

5. **When to stop:** Diminishing returns — last N improvement cycles produced no skill revisions.

### Format

- Improvement loop flowchart
- Anti-overfitting checklist
- Skill revision log template
- Example from HDD project: Phase 3 → VERIFY step → Phase 3b → monolithic guidance

## Decisions

- **Self-contained:** No required dependency on writing-skills or superpowers. Includes enough context to stand alone.
- **Default personas + customization:** Ship three proven judge personas but teach how to design domain-specific ones.
- **Progression template:** Provide the 3-phase template (compliance → stress → quality) as a recommended starting point.
- **Subdirectory repo:** Lives under `experiment-driven-skill-development/` in the HDD project since the sandbox is ephemeral outside this directory.

## Non-Goals

- Replacing writing-skills (which covers RED-GREEN-REFACTOR for initial skill creation)
- Prescribing specific task domains
- Automating the loop (the skills guide a human/agent through the process)

## Testing Plan

Per the writing-skills Iron Law, each skill must be tested before deployment:

1. **blind-skill-assessment:** Give a subagent two code versions and the skill. Does it randomize labels, use personas, score correctly, require baseline?
2. **experiment-set-design:** Give a subagent a new skill to test. Does it design a proper task set with baselines and phase progression?
3. **iterative-skill-refinement:** Give a subagent a skill that fails blind review. Does it follow the improvement loop, watch for overfitting, track revisions?
