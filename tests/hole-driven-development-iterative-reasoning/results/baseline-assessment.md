# Baseline Assessment: Iterative-Reasoning Skill — Scenario 1 (CSV Parser)

## Grade: FAIL (expected — this is baseline WITHOUT skill)

## Behavior observed

Agent wrote the complete implementation in one pass:
- Identified sub-problems (row splitting, field parsing with quotes, header mapping) in reasoning
- But wrote ALL of them at once — no holes, no iterative decomposition
- No visible HOLE markers in the file at any point
- Final code: 17 lines, complete, correct

Key behavior: Agent did identify the same sub-problems that HDD would create as holes (row splitting, quote-aware field parsing, header mapping), but it wrote them all in a single Write call.

## Rationalizations observed

None (agent wasn't asked to use HDD). This confirms baseline: the default approach is "think it through, write it all at once."

## Conclusion

The iterative-reasoning skill needs to redirect this behavior toward:
1. Writing a skeleton with HOLE markers (e.g., `raise NotImplementedError("HOLE_1: parse fields respecting quotes")`)
2. Making each hole visible in the file before filling
3. Filling one hole at a time with explicit reasoning about its contract
4. Optionally running a type checker if available
