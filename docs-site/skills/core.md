# Core Skill

The foundational skill that defines HDD philosophy. Both extending skills require this.

## Overview

Implement top-down by decomposition. Start with the outermost structure, leave **holes** for unknown parts, then fill each hole iteratively — possibly introducing smaller holes — until none remain.

**Core principle:** Never write a complete implementation in one pass. Decompose first, fill later.

## The Loop

```
1. Receive intention (type signature, spec, or description)
2. Write skeleton to the file with HOLES for each unknown sub-problem
3. Pick the most constrained hole (fewest valid fills)
4. Determine what the hole needs (type, contract, inputs available)
5. Fill ONE hole in the file — introduce sub-holes if the fill is itself complex
6. VERIFY the fill against previously filled code:
   - Shared mutable state: is access synchronized?
   - Lifecycle: are acquire/release scopes matched across holes?
   - Error/cancel paths: do they clean up resources from other holes?
   If any check fails, fix before proceeding.
7. Repeat from 3 until no holes remain
8. REVIEW-ALL: before declaring done, re-read the complete implementation:
   - State transitions that span multiple fills
   - Resource acquired in one fill, released in another
   - Error paths that cross fill boundaries
   - Loop invariants depending on multiple fills
   Fix any systemic bug the per-hole VERIFY could not catch.
```

## Key Rules

**Holes must be visible.** Write holes to the file, not just in your reasoning. Each iteration edits the file — the human should see the skeleton evolve.

**One hole per iteration.** Fill exactly one hole, then reassess. Do not batch-fill.

**Most constrained first.** When multiple holes exist, fill the one with the narrowest contract — fewest possible implementations, least likely to get wrong.

**When ambiguous** — multiple equally valid fills — STOP and ask the human.

**When NOT to decompose further.** Some algorithms are inherently monolithic — dual-cursor walks, coroutine-style loops, complex state machines with tightly coupled transitions. If the state cannot be cleanly partitioned across hole boundaries, keep it as a single hole with internal comments for structure.

## Success Criterion

No holes remain, the code satisfies the original intention, the REVIEW-ALL pass found no systemic bugs, and no cross-hole interaction bugs remain.

## What This Skill Does NOT Cover

How to determine what a hole needs — that depends on the extending skill:

- [Compiler Loop](compiler-loop.md): runs compiler, reads diagnostics
- [Iterative Reasoning](iterative-reasoning.md): Claude reasons about contracts

## Red Flags

- Writing a complete implementation without first creating holes
- Keeping holes in your head instead of writing them to the file
- Filling multiple holes in a single step
- Skipping hole analysis ("I already know the answer")
- Writing the final code directly and claiming you "decomposed mentally"
- Skipping the VERIFY step after filling ("it's obviously correct in context")
