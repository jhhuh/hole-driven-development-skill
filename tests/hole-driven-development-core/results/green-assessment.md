# GREEN Assessment: Core Skill — Scenario 1 (TOC Generator)

## Grade: PARTIAL

## Behavior observed

Agent DID follow the HDD decomposition approach:
- Identified 4 holes: parse heading, generate slug, deduplicate slug, format entry
- Reasoned about fill order (most constrained first)
- Filled holes one at a time across 12 tool calls
- Used correct constraint reasoning: "Format is most constrained (single valid output given inputs)"

Agent DID NOT:
- Write intermediate states with visible holes to the file (the file was written with all holes already filled — the holes only existed in the agent's reasoning)
- The final file looks identical to the baseline — you can't tell it was developed with HDD

## Root cause

The core skill says "write skeleton with HOLES" but doesn't enforce that holes must be **visible in the file** as explicit markers. The agent kept holes in its head and wrote the final code.

This is the core skill's responsibility if being used standalone, but when used with an extending skill (compiler-loop or iterative-reasoning), those extending skills handle the visible-hole mechanism. The core skill alone is ambiguous on this point.

## Skill revision needed

Two options:
1. Core skill requires visible holes in the file (changes core's scope)
2. Core skill stays abstract; extending skills enforce visible holes (current architecture)

Recommend option 2 — core stays abstract. The "visible holes" behavior is the extending skills' job. But core should note that holes must be trackable (not just in your head).

## Rationalizations observed

None — agent followed the process. The gap is in the skill spec, not agent compliance.
