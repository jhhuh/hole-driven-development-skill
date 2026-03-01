# Scenario: Implement myFoldr using typed holes

## Setup
There is a Haskell file at tests/hole-driven-development/test-project/Lib.hs
with a type signature for myFoldr and a single typed hole.

## Prompt
Use hole-driven development to implement myFoldr. Run GHC to get
hole diagnostics and iteratively fill holes until the code compiles.

## Expected WITHOUT skill (baseline)
Agent writes the complete implementation directly without running GHC
or using typed hole feedback.

## Expected WITH skill
Agent runs GHC, reads hole diagnostics, fills one hole at a time
(possibly introducing new holes), repeats until compilation succeeds.
