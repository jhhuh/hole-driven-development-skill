# B1: group_by -- HDD Iterative Reasoning Assessment

## 1. Number of holes created

2 holes:
- **HOLE_1**: Initialize accumulator (`dict[str, list[dict]]`)
- **HOLE_2**: Iterate items and populate accumulator (`dict[str, list[dict]]`)

## 2. Fill order and reasoning

### Fill 1: HOLE_1 (Initialize accumulator)

- **Why first**: Most constrained. HOLE_2 depends on the accumulator existing; HOLE_1 has no dependencies.
- **Reasoning**: Produces `dict[str, list[dict]]`. No inputs needed. Must be mutable for HOLE_2 to populate. Fill: `result: dict[str, list[dict]] = {}`.

### Fill 2: HOLE_2 (Iterate and populate)

- **Why second**: Only remaining hole. Depends on `result` from HOLE_1.
- **Reasoning**: Inputs available: `items`, `key`, `result`. For each item, extract `item[key]` as group key, append item to that group. `setdefault` handles missing keys cleanly. Must return `result`. Fill: for-loop with `setdefault` + `append`, then `return result`.

## 3. Were visible HOLE markers used in the file?

Yes. Both holes were written as `raise NotImplementedError("HOLE_N: ...")` in the source file before any filling began. The file with holes was committed via the Write tool, then each hole was filled via the Edit tool in sequence.

## 4. Total tool calls

- **Write**: 2 (skeleton with holes, assessment)
- **Edit**: 2 (fill HOLE_1, fill HOLE_2)
- **Read**: 1 (verify final file)
- **Bash**: 3 (mkdir, find python, run tests)

**Total: 8 tool calls**

## 5. Observations

This is a trivially simple function (the final implementation is 4 lines of logic). The skill's requirement of "at least 2 visible HOLE markers" forces decomposition that, for this problem, maps naturally to the two conceptual steps: (1) create the container, (2) fill it. The decomposition is not artificial -- these are genuinely distinct concerns -- but the reasoning overhead far exceeds the implementation complexity. This is expected for a calibration benchmark (B1).
