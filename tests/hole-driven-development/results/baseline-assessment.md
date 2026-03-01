# Baseline Assessment: Compiler-Loop Skill — Scenario 1 (myFoldr)

## Grade: N/A (tainted baseline)

## Behavior observed

Agent DID use the compiler loop correctly:
- 3 compilation rounds (initial hole → case split → fill arguments → verify)
- Read hole diagnostics at each step (hole type, valid fits, relevant bindings)
- Filled one hole at a time
- Used GHC's "Valid hole fits" to guide decisions
- Recognized when GHC's suggestions were misleading (z vs recursive call)

## Problem with this baseline

The prompt explicitly told the agent: "Use hole-driven development to implement myFoldr. Run GHC to get hole diagnostics and iteratively fill holes until the code compiles."

This means the agent was INSTRUCTED to follow HDD — the baseline doesn't test natural behavior. A proper baseline would just say "implement myFoldr" without mentioning HDD or typed holes.

However, this test is still informative:
- Shows the agent CAN interact with GHC's typed hole system
- Shows the agent understands hole diagnostics
- The compiler-loop skill's job is to make this AUTOMATIC, not to teach it from scratch

## Conclusion

The compiler-loop skill needs to:
1. Trigger automatically when Haskell files with typed holes are present
2. Enforce the compile → read → fill loop discipline
3. Handle compiler invocation details (cabal vs ghc detection)
4. Enforce one-hole-at-a-time filling (agent batch-filled in iteration 2)

Note: Agent modified the test-project Lib.hs during the baseline. It needs to be restored for future tests.
