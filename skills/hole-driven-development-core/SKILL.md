---
name: hole-driven-development-core
description: Use when implementing functions or modules top-down by decomposing into typed holes, filling iteratively from most constrained to least
---

# Hole Driven Development — Core

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
```

**Holes must be visible.** Write holes to the file, not just in your reasoning. Each iteration of the loop edits the file — the human should see the skeleton evolve in their editor.

**One hole per iteration.** Fill exactly one hole, then reassess. Do not batch-fill.

**Most constrained first.** When multiple holes exist, fill the one with the narrowest contract — it has the fewest possible implementations, so you're least likely to get it wrong.

**When ambiguous** — multiple equally valid fills — STOP and ask the human.

## Success Criterion

No holes remain, the code satisfies the original intention, and no cross-hole interaction bugs remain.

## What This Skill Does NOT Cover

- **How** to determine what a hole needs — that depends on the extending skill:
  - Compiler-feedback loop: `hole-driven-development` (runs compiler, reads diagnostics)
  - Iterative reasoning: `hole-driven-development-iterative-reasoning` (Claude reasons about contracts)

## Red Flags — STOP

- Writing a complete implementation without first creating holes
- Keeping holes in your head instead of writing them to the file
- Filling multiple holes in a single step
- Skipping hole analysis ("I already know the answer")
- Writing the final code directly and claiming you "decomposed mentally"
- Creating artificial decomposition for trivial one-liners (1-2 lines of obvious code)
- Skipping the VERIFY step after filling ("it's obviously correct in context")

**If you catch yourself doing any of these: STOP. Delete. Start with holes in the file.**
