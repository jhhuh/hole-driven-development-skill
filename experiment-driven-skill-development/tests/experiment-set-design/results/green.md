# GREEN Test: Experiment Set Design (With Skill Loaded)

## Scenario
Same as baseline: design a test plan for the HDD skill (4 rules listed).

## Observed Behavior — Skill Compliance

### Baseline Requirement
**PASS.** Agent stated: "Every task is run twice: 1) Baseline run — same prompt,
same task, no skill loaded. 2) Skill run — same prompt, same task, skill loaded."
Marked as NON-NEGOTIABLE. Controlled for model, temperature, system prompt.

### Task Selection Checklist
**PASS.** Agent used the 4-checkbox format from the skill for each task, verifying
all criteria. Also included a diversity check table at the end.

5 tasks designed:
- T1: Haskell AVL tree (data structures)
- T2: Rust work-stealing deque (concurrency)
- T3: Haskell HTTP parser (parsing/networking)
- T4: Go CLI tool (systems)
- T5: Python data pipeline (data engineering)

### Three-Phase Progression
**PASS.** Agent designed all three phases:
- Phase 1: Compliance — 7 rules checked as PASS/FAIL per task (35 checks)
- Phase 2: Stress — competing instructions, time pressure, partial solutions,
  large scope, trivial sub-task trap
- Phase 3: Quality — baseline vs skill, blind 3-persona review, 4 dimensions

### Phase Advancement
**PASS.** Agent specified: "All PASS before advancing. Any FAIL: improve skill,
re-run current phase."

### Task Set Diversity
**PASS.** Agent included diversity check:
- 5 domains (data structures, concurrency, parsing, CLI, data engineering)
- 3 complexity tiers (single module, multi-module, concurrent)
- 4 languages (Haskell, Rust, Go, Python)

### Revision Tracking
**PASS.** Agent included revision tracking table with: skill version (git hash),
tasks run, phase, results, what changed, model, timestamp.

### Anti-Overfitting
**PASS.** "After 2 improvement cycles on the same task set, add at least 1 new
task... to prevent overfitting to the existing 5."

## Improvement Over Baseline

| Behavior | Baseline | GREEN |
|----------|----------|-------|
| Baseline as governing principle | Implicit (contrastive design) | Explicit, non-negotiable |
| Anti-overfitting guidance | Not mentioned | Task rotation rule included |
| Phase progression | No (all at same level) | Yes (Compliance→Stress→Quality) |
| Assessment method variation | No (all transcript-based) | Yes (PASS/FAIL → blind review) |
| Revision tracking | Not mentioned | Full tracking table |
| Practical sample sizes | 72-120 runs | 5 tasks per phase |

## Skill Compliance: All 6 key behaviors present. RED gaps fully addressed.

## Bonus: Agent went beyond minimum
- Identified 7 HDD rules (not just the 4 listed in scenario) by reading actual skills
- Designed stressor variants per-task (not generic)
- Included ambiguity injection variant for R4
- Red flag self-audit checklist at the end
