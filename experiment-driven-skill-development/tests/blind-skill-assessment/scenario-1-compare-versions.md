# Scenario: Compare Two Implementations

You are given two implementations of a three-way text merge algorithm.
Compare them and tell me which is better.

## Version A

```python
"""
Three-way text merge algorithm (LCS-based), similar to git's merge.

merge3(base, ours, theirs) -> (merged_text: str, has_conflicts: bool)
"""

from typing import List, Tuple, NamedTuple


class Hunk(NamedTuple):
    base_start: int
    base_end: int
    other_lines: List[str]


def _lcs_table(a: List[str], b: List[str]) -> List[List[int]]:
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    return table


def _extract_hunks(base: List[str], other: List[str], table: List[List[int]]) -> List[Hunk]:
    matches: List[Tuple[int, int]] = []
    i, j = len(base), len(other)
    while i > 0 and j > 0:
        if base[i - 1] == other[j - 1]:
            matches.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif table[i - 1][j] >= table[i][j - 1]:
            i -= 1
        else:
            j -= 1
    matches.reverse()

    hunks: List[Hunk] = []
    prev_base = 0
    prev_other = 0
    for bi, oi in matches:
        if bi > prev_base or oi > prev_other:
            hunks.append(Hunk(prev_base, bi, list(other[prev_other:oi])))
        prev_base = bi + 1
        prev_other = oi + 1

    if prev_base < len(base) or prev_other < len(other):
        hunks.append(Hunk(prev_base, len(base), list(other[prev_other:])))

    return hunks


def _merge_hunks(
    base: List[str],
    hunks_ours: List[Hunk],
    hunks_theirs: List[Hunk],
) -> Tuple[List[str], bool]:
    output: List[str] = []
    has_conflicts = False
    base_pos = 0
    oi = 0
    ti = 0

    while base_pos <= len(base):
        o_hunk = hunks_ours[oi] if oi < len(hunks_ours) else None
        t_hunk = hunks_theirs[ti] if ti < len(hunks_theirs) else None

        if o_hunk is None and t_hunk is None:
            output.extend(base[base_pos:])
            break

        o_start = o_hunk.base_start if o_hunk else len(base) + 1
        t_start = t_hunk.base_start if t_hunk else len(base) + 1
        next_event = min(o_start, t_start)

        if next_event > base_pos:
            output.extend(base[base_pos:next_event])
            base_pos = next_event

        both_active = (
            o_hunk is not None
            and t_hunk is not None
            and (
                (o_hunk.base_start < t_hunk.base_end and t_hunk.base_start < o_hunk.base_end)
                or (o_hunk.base_start == o_hunk.base_end == t_hunk.base_start == t_hunk.base_end)
            )
        )

        if both_active:
            assert o_hunk is not None and t_hunk is not None
            if (o_hunk.base_start == t_hunk.base_start
                    and o_hunk.base_end == t_hunk.base_end
                    and o_hunk.other_lines == t_hunk.other_lines):
                output.extend(o_hunk.other_lines)
                base_pos = o_hunk.base_end
                oi += 1
                ti += 1
                continue

            conflict_base_start = min(o_hunk.base_start, t_hunk.base_start)
            conflict_base_end = max(o_hunk.base_end, t_hunk.base_end)
            oi_first = oi
            ti_first = ti
            oi += 1
            ti += 1
            expanded = True
            while expanded:
                expanded = False
                while oi < len(hunks_ours) and hunks_ours[oi].base_start < conflict_base_end:
                    if hunks_ours[oi].base_end > conflict_base_end:
                        conflict_base_end = hunks_ours[oi].base_end
                        expanded = True
                    oi += 1
                while ti < len(hunks_theirs) and hunks_theirs[ti].base_start < conflict_base_end:
                    if hunks_theirs[ti].base_end > conflict_base_end:
                        conflict_base_end = hunks_theirs[ti].base_end
                        expanded = True
                    ti += 1

            ours_lines: List[str] = []
            pos = conflict_base_start
            for idx in range(oi_first, oi):
                h = hunks_ours[idx]
                ours_lines.extend(base[pos:h.base_start])
                ours_lines.extend(h.other_lines)
                pos = h.base_end
            ours_lines.extend(base[pos:conflict_base_end])

            theirs_lines: List[str] = []
            pos = conflict_base_start
            for idx in range(ti_first, ti):
                h = hunks_theirs[idx]
                theirs_lines.extend(base[pos:h.base_start])
                theirs_lines.extend(h.other_lines)
                pos = h.base_end
            theirs_lines.extend(base[pos:conflict_base_end])

            if ours_lines == theirs_lines:
                output.extend(ours_lines)
            else:
                has_conflicts = True
                output.append("<<<<<<< OURS\n")
                output.extend(ours_lines)
                output.append("=======\n")
                output.extend(theirs_lines)
                output.append(">>>>>>> THEIRS\n")

            base_pos = conflict_base_end

        elif o_hunk is not None and o_start <= t_start:
            output.extend(o_hunk.other_lines)
            base_pos = o_hunk.base_end
            oi += 1

        elif t_hunk is not None:
            output.extend(t_hunk.other_lines)
            base_pos = t_hunk.base_end
            ti += 1

        else:
            if base_pos < len(base):
                output.append(base[base_pos])
                base_pos += 1
            else:
                break

    return output, has_conflicts


def merge3(base_text: str, ours_text: str, theirs_text: str) -> Tuple[str, bool]:
    base_lines = base_text.splitlines(keepends=True)
    ours_lines = ours_text.splitlines(keepends=True)
    theirs_lines = theirs_text.splitlines(keepends=True)

    table_ours = _lcs_table(base_lines, ours_lines)
    hunks_ours = _extract_hunks(base_lines, ours_lines, table_ours)

    table_theirs = _lcs_table(base_lines, theirs_lines)
    hunks_theirs = _extract_hunks(base_lines, theirs_lines, table_theirs)

    merged_lines, has_conflicts = _merge_hunks(base_lines, hunks_ours, hunks_theirs)
    return "".join(merged_lines), has_conflicts
```

## Version B

```python
"""
Three-way text merge, like git's merge algorithm.

Given three versions of a file:
  - base: the common ancestor
  - ours: our changes from base
  - theirs: their changes from base

Produce a merged result that:
  1. Keeps changes from both sides when they don't conflict
  2. Detects conflicts when both sides changed the same region
  3. Produces conflict markers (<<<<<<< OURS / ======= / >>>>>>> THEIRS)
  4. Handles insertions, deletions, and modifications
  5. Adjacent changes (touching but non-overlapping) should NOT conflict

Requirements:
  - Implement the diff algorithm (longest common subsequence based)
  - Compute the diff between base->ours and base->theirs
  - Align the two diffs to find overlapping change regions
  - Produce merged output with conflict markers where needed
  - Return (merged_text: str, has_conflicts: bool)

Edge cases:
  - Both sides make the same change -> no conflict (take either)
  - One side deletes a line, other modifies it -> conflict
  - Both sides insert at the same point -> conflict
  - Empty files
  - One side unchanged -> take the other side's changes entirely
"""


def _lcs_table(a: list[str], b: list[str]) -> list[list[int]]:
    """Build the LCS dynamic programming table."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp


def _compute_blocks(base: list[str], other: list[str]) -> list[tuple[str, int, int, int, int]]:
    dp = _lcs_table(base, other)

    matches = []
    i, j = len(base), len(other)
    while i > 0 and j > 0:
        if base[i - 1] == other[j - 1]:
            matches.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    matches.reverse()

    blocks = []
    bi, oi = 0, 0
    for bm, om in matches:
        if bi < bm or oi < om:
            blocks.append(('replace', bi, bm, oi, om))
        blocks.append(('equal', bm, bm + 1, om, om + 1))
        bi, oi = bm + 1, om + 1
    if bi < len(base) or oi < len(other):
        blocks.append(('replace', bi, len(base), oi, len(other)))

    return blocks


def _collapse_equal(blocks: list[tuple[str, int, int, int, int]]) -> list[tuple[str, int, int, int, int]]:
    if not blocks:
        return blocks
    out = [blocks[0]]
    for b in blocks[1:]:
        prev = out[-1]
        if b[0] == prev[0]:
            out[-1] = (prev[0], prev[1], b[2], prev[3], b[4])
        else:
            out.append(b)
    return out


def merge3(base: str, ours: str, theirs: str) -> tuple[str, bool]:
    if ours == theirs:
        return (ours, False)
    if base == ours:
        return (theirs, False)
    if base == theirs:
        return (ours, False)

    base_lines = base.splitlines(True)
    ours_lines = ours.splitlines(True)
    theirs_lines = theirs.splitlines(True)

    ours_blocks = _collapse_equal(_compute_blocks(base_lines, ours_lines))
    theirs_blocks = _collapse_equal(_compute_blocks(base_lines, theirs_lines))

    def to_regions(blocks, other_lines):
        regions = []
        for tag, bs, be, os, oe in blocks:
            regions.append((bs, be, other_lines[os:oe], tag == 'replace'))
        return regions

    ours_regions = to_regions(ours_blocks, ours_lines)
    theirs_regions = to_regions(theirs_blocks, theirs_lines)

    def split_at(regions, base_lines, cut_points):
        result = []
        for region in regions:
            bs, be, repl, changed = region
            cuts = [c for c in cut_points if bs < c < be]
            if not cuts:
                result.append(region)
                continue
            if not changed:
                prev = bs
                for c in cuts:
                    result.append((prev, c, base_lines[prev:c], False))
                    prev = c
                result.append((prev, be, base_lines[prev:be], False))
            else:
                result.append(region)
        return result

    def boundaries(regions):
        pts = set()
        for bs, be, _, _ in regions:
            pts.add(bs)
            pts.add(be)
        return pts

    all_cuts = sorted(boundaries(ours_regions) | boundaries(theirs_regions))
    ours_regions = split_at(ours_regions, base_lines, all_cuts)
    theirs_regions = split_at(theirs_regions, base_lines, all_cuts)

    output: list[str] = []
    has_conflicts = False

    oi, ti = 0, 0

    while oi < len(ours_regions) or ti < len(theirs_regions):
        if oi < len(ours_regions) and ti < len(theirs_regions):
            obs, obe = ours_regions[oi][0], ours_regions[oi][1]
            tbs, tbe = theirs_regions[ti][0], theirs_regions[ti][1]

            if obs == tbs and obe == tbe:
                o_repl, o_changed = ours_regions[oi][2], ours_regions[oi][3]
                t_repl, t_changed = theirs_regions[ti][2], theirs_regions[ti][3]

                if not o_changed and not t_changed:
                    output.extend(o_repl)
                elif o_changed and not t_changed:
                    output.extend(o_repl)
                elif not o_changed and t_changed:
                    output.extend(t_repl)
                else:
                    if o_repl == t_repl:
                        output.extend(o_repl)
                    else:
                        has_conflicts = True
                        output.append('<<<<<<< OURS\n')
                        output.extend(_ensure_newline(o_repl))
                        output.append('=======\n')
                        output.extend(_ensure_newline(t_repl))
                        output.append('>>>>>>> THEIRS\n')
                oi += 1
                ti += 1
                continue

            o_group, t_group, oi, ti = _collect_overlap_group(
                ours_regions, theirs_regions, oi, ti
            )

            o_any_changed = any(r[3] for r in o_group)
            t_any_changed = any(r[3] for r in t_group)

            o_repl = _flatten_repl(o_group)
            t_repl = _flatten_repl(t_group)

            if not o_any_changed and not t_any_changed:
                output.extend(o_repl)
            elif o_any_changed and not t_any_changed:
                output.extend(o_repl)
            elif not o_any_changed and t_any_changed:
                output.extend(t_repl)
            else:
                if o_repl == t_repl:
                    output.extend(o_repl)
                else:
                    has_conflicts = True
                    output.append('<<<<<<< OURS\n')
                    output.extend(_ensure_newline(o_repl))
                    output.append('=======\n')
                    output.extend(_ensure_newline(t_repl))
                    output.append('>>>>>>> THEIRS\n')
            continue

        elif oi < len(ours_regions):
            output.extend(ours_regions[oi][2])
            oi += 1
        else:
            output.extend(theirs_regions[ti][2])
            ti += 1

    merged = ''.join(output)
    return (merged, has_conflicts)


def _collect_overlap_group(
    ours_regions, theirs_regions, oi, ti
) -> tuple[list, list, int, int]:
    o_group = []
    t_group = []

    group_end = 0

    if oi < len(ours_regions):
        o_group.append(ours_regions[oi])
        group_end = max(group_end, ours_regions[oi][1])
        oi += 1
    if ti < len(theirs_regions):
        t_group.append(theirs_regions[ti])
        group_end = max(group_end, theirs_regions[ti][1])
        ti += 1

    changed = True
    while changed:
        changed = False
        while oi < len(ours_regions) and ours_regions[oi][0] < group_end:
            o_group.append(ours_regions[oi])
            group_end = max(group_end, ours_regions[oi][1])
            oi += 1
            changed = True
        while ti < len(theirs_regions) and theirs_regions[ti][0] < group_end:
            t_group.append(theirs_regions[ti])
            group_end = max(group_end, theirs_regions[ti][1])
            ti += 1
            changed = True

    return o_group, t_group, oi, ti


def _flatten_repl(group: list[tuple]) -> list[str]:
    lines = []
    for _, _, repl, _ in group:
        lines.extend(repl)
    return lines


def _ensure_newline(lines: list[str]) -> list[str]:
    if not lines:
        return lines
    if lines[-1] and not lines[-1].endswith('\n'):
        return lines[:-1] + [lines[-1] + '\n']
    return lines
```

## Instructions

Evaluate both versions thoroughly. Which one is better? Provide your
assessment with specific reasoning.
