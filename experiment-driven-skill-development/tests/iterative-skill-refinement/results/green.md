# GREEN Test: Iterative Skill Refinement (With Skill Loaded)

## Scenario
Same as baseline: given Phase 3 results (Baseline 4, HDD 1), specific bugs,
and root cause pattern. Asked: "How should I improve the skill?"

## Observed Behavior — Skill Compliance

### Step 1: ASSESS
**PASS.** Agent summarized data with table: Bug Hunter avg -2.0, Architect +0.4,
Pragmatist +0.6. Framed as "skill loses overall because bug scores dominate."

### Step 2: DIAGNOSE — Root Cause
**PASS.** Agent identified root cause CLASS, not just individual bugs:
- "Cross-hole interaction bugs" (shared state, resource lifecycle, semantic invariants)
- Explained WHY: "The skill had no step between filling a hole and moving to the
  next that asked: does this fill interact correctly with previously filled holes?"
- Also identified secondary cause: over-decomposition of tightly coupled state (H3)

### Step 3: TRIAGE — Ranked by Breadth
**PASS.** Agent created a ranked table:
1. No cross-hole verification (5/5 experiments affected — widest impact)
2. No guidance on when NOT to decompose (1/5)
3. Missing REVIEW-ALL (secondary to #1)

Decided: "Fix #1 first. It affects all 5 experiments."

### Step 4: EDIT — Targeted Changes
**PASS.** Three specific edits, each with:
- Exact files to modify
- Exact location in the loop
- Exact text to add
- Explanation of WHY it's structural, not task-specific

### Step 5: RE-RUN — Re-experimentation Plan
**PASS.** Agent planned:
- Phase 3b: Same 5 experiments with improved skill
- Phase 3c: 2-3 NEW tasks (concurrent web scraper, incremental parser, consensus
  simulator) to verify generalization

### Step 6: ANTI-OVERFITTING — Checklist
**PASS.** Agent completed all 4 checks from the skill's table:
- "Would this help on a different task? Yes — structural improvement"
- "General step, not task-specific? Yes"
- "New tasks planned? Phase 3c plans new tasks"
- "Judge rotation planned? Security Reviewer or Performance Engineer if cycle 2"
- Litmus test: "Adds a structural step catching a class of bugs — genuine"

### Step 7: CONVERGENCE
**PASS.** Agent defined 4 specific criteria:
1. HDD wins 4/5 original + 2/3 new tasks
2. New tasks reveal no new failure modes
3. Last 2 cycles produce no revisions
4. Gains per cycle diminishing

Also defined early termination: "If Phase 3b fails, don't run Phase 3c."

### Step 8: REVISION LOG
**PASS.** Agent created revision log with 3 pending entries, each with
"Triggered by" (specific data) and "Validated by" (planned experiment).

## Improvement Over Baseline

| Behavior | Baseline | GREEN |
|----------|----------|-------|
| Structured improvement loop | No (jumped to fixes) | Yes (7-step loop) |
| Re-experimentation plan | Not mentioned | Phase 3b + 3c planned |
| Overfitting warning | Not mentioned | Full 4-check + litmus test |
| Revision tracking | Not mentioned | 3-entry log with triggers/validation |
| Severity triage | Equal weight | Ranked by breadth (5/5 → 1/5) |
| Baseline comparison framing | "Fewer bugs" | "Beats baseline" |
| Convergence criteria | Not defined | 4 specific stop conditions |

## Skill Compliance: All 7 loop steps followed + revision log.

## Notable
- Agent read ALL THREE actual HDD skills for context (not just the scenario data)
- Proposed the same VERIFY/monolithic/REVIEW-ALL fixes that were actually implemented —
  this confirms the skill guides toward the right answer
- Anti-overfitting checklist was completed thoughtfully, not perfunctorily
