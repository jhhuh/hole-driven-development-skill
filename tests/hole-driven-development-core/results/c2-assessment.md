# C2 Assessment: process_order

## What I did

I recognized that HDD decomposition was not needed and wrote the implementation directly. The function is a trivial 3-line pipeline composing three provided helpers in sequence: `validate_order` -> `charge_payment` -> `generate_receipt`. Each call has exactly one valid input (the output of the previous step), making the entire function fully determined with no ambiguity or decision points.

The skill explicitly flags "Creating artificial decomposition for trivial one-liners (1-2 lines of obvious code)" as a red flag. While this is 3 lines, it falls in the same category: a linear pipeline where each step is a single function call with a single obvious argument. Introducing holes here (e.g., `validated = ???`, `charged = ???`, `result = ???`) would be artificial -- each "hole" has exactly one valid fill that is immediately obvious from the types.

## Why

- The decomposition was already done by the task itself (three separate helper functions).
- The composition has zero branching, zero ambiguity, and zero design decisions.
- Every "hole" would have exactly one valid fill, making the HDD loop degenerate into busywork.
- The skill's red-flag list exists precisely to prevent this kind of artificial ceremony.

## Tool calls / iterations

- 1 write for helpers file
- 1 write for implementation (direct, no holes)
- 2 bash calls for verification (1 failed due to module path, 1 succeeded)
- 1 write for this assessment
- **Total: 5 tool calls, 1 implementation iteration (no hole-filling loop)**
