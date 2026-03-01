"""
Three-way text merge algorithm (LCS-based), similar to git's merge.

merge3(base, ours, theirs) -> (merged_text: str, has_conflicts: bool)
"""

from typing import List, Tuple, NamedTuple


class Hunk(NamedTuple):
    """A contiguous region of change between two texts.

    base_start: starting line index in base (inclusive)
    base_end:   ending line index in base (exclusive)
    other_lines: the replacement lines from the other side
    """
    base_start: int
    base_end: int
    other_lines: List[str]


def _lcs_table(a: List[str], b: List[str]) -> List[List[int]]:
    """Build the LCS dynamic-programming table for sequences a and b.

    Returns a (len(a)+1) x (len(b)+1) table where table[i][j] is the length
    of the LCS of a[:i] and b[:j].
    """
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
    """Walk the LCS table to extract contiguous change hunks.

    A hunk groups consecutive non-matching lines. Lines matching via LCS
    are 'equal' regions; everything between equal regions is a hunk.

    Returns hunks sorted by base_start.
    """
    # Backtrack through LCS table to get matched pairs (base_idx, other_idx)
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

    # Walk matched pairs to find gaps (hunks)
    hunks: List[Hunk] = []
    prev_base = 0
    prev_other = 0
    for bi, oi in matches:
        if bi > prev_base or oi > prev_other:
            hunks.append(Hunk(prev_base, bi, list(other[prev_other:oi])))
        prev_base = bi + 1
        prev_other = oi + 1

    # Trailing hunk after the last match
    if prev_base < len(base) or prev_other < len(other):
        hunks.append(Hunk(prev_base, len(base), list(other[prev_other:])))

    return hunks


def _merge_hunks(
    base: List[str],
    hunks_ours: List[Hunk],
    hunks_theirs: List[Hunk],
) -> Tuple[List[str], bool]:
    """Merge two hunk lists against the same base, producing output lines.

    Dual-cursor state machine: walk through base positions, consuming hunks
    from both sides. Detect overlaps, apply non-conflicting changes, emit
    conflict markers for true conflicts.

    Returns (merged_lines, has_conflicts).
    """
    output: List[str] = []
    has_conflicts = False
    base_pos = 0
    oi = 0  # cursor into hunks_ours
    ti = 0  # cursor into hunks_theirs

    while base_pos <= len(base):
        # --- Determine next hunk from each side (or sentinel past end) ---
        o_hunk = hunks_ours[oi] if oi < len(hunks_ours) else None
        t_hunk = hunks_theirs[ti] if ti < len(hunks_theirs) else None

        # If no more hunks on either side, emit remaining base and stop
        if o_hunk is None and t_hunk is None:
            output.extend(base[base_pos:])
            break

        # --- Find the next event position ---
        o_start = o_hunk.base_start if o_hunk else len(base) + 1
        t_start = t_hunk.base_start if t_hunk else len(base) + 1
        next_event = min(o_start, t_start)

        # Emit unchanged base lines up to next event
        if next_event > base_pos:
            output.extend(base[base_pos:next_event])
            base_pos = next_event

        # --- Check for overlap between current hunks ---
        # Two hunks overlap if their base ranges intersect: start_a < end_b and start_b < end_a
        # Adjacent (touching) ranges do NOT overlap: [1,3) and [3,5) don't intersect
        # Special case: zero-width hunks (pure insertions) at the same position DO overlap
        both_active = (
            o_hunk is not None
            and t_hunk is not None
            and (
                (o_hunk.base_start < t_hunk.base_end and t_hunk.base_start < o_hunk.base_end)
                or (o_hunk.base_start == o_hunk.base_end == t_hunk.base_start == t_hunk.base_end)
            )
        )

        if both_active:
            # --- OVERLAP: both sides modify intersecting base regions ---
            assert o_hunk is not None and t_hunk is not None  # for type checker
            # Identical change shortcut
            if (o_hunk.base_start == t_hunk.base_start
                    and o_hunk.base_end == t_hunk.base_end
                    and o_hunk.other_lines == t_hunk.other_lines):
                output.extend(o_hunk.other_lines)
                base_pos = o_hunk.base_end
                oi += 1
                ti += 1
                continue

            # Compute the union base range of all overlapping hunks
            conflict_base_start = min(o_hunk.base_start, t_hunk.base_start)
            conflict_base_end = max(o_hunk.base_end, t_hunk.base_end)
            # Record where the conflict hunks begin in each list
            oi_first = oi
            ti_first = ti
            # Advance past the initial pair
            oi += 1
            ti += 1
            # Expand if further hunks from either side overlap the conflict region
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

            # Reconstruct each side's view of the conflict region
            # Build ours_lines: apply ours hunks within conflict region, keep base elsewhere
            ours_lines: List[str] = []
            pos = conflict_base_start
            for idx in range(oi_first, oi):
                h = hunks_ours[idx]
                ours_lines.extend(base[pos:h.base_start])
                ours_lines.extend(h.other_lines)
                pos = h.base_end
            ours_lines.extend(base[pos:conflict_base_end])

            # Build theirs_lines: apply theirs hunks within conflict region, keep base elsewhere
            theirs_lines: List[str] = []
            pos = conflict_base_start
            for idx in range(ti_first, ti):
                h = hunks_theirs[idx]
                theirs_lines.extend(base[pos:h.base_start])
                theirs_lines.extend(h.other_lines)
                pos = h.base_end
            theirs_lines.extend(base[pos:conflict_base_end])

            # If reconstructed sides match, it's not a real conflict
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
            # oi and ti already advanced past conflict region by the expansion loop

        elif o_hunk is not None and o_start <= t_start:
            # --- Only ours has a hunk at this position ---
            output.extend(o_hunk.other_lines)
            base_pos = o_hunk.base_end
            oi += 1

        elif t_hunk is not None:
            # --- Only theirs has a hunk at this position ---
            output.extend(t_hunk.other_lines)
            base_pos = t_hunk.base_end
            ti += 1

        else:
            # Should not reach here, but guard against infinite loop
            if base_pos < len(base):
                output.append(base[base_pos])
                base_pos += 1
            else:
                break

    return output, has_conflicts


def merge3(base_text: str, ours_text: str, theirs_text: str) -> Tuple[str, bool]:
    """Three-way merge of text strings.

    Returns (merged_text, has_conflicts).
    """
    base_lines = base_text.splitlines(keepends=True)
    ours_lines = ours_text.splitlines(keepends=True)
    theirs_lines = theirs_text.splitlines(keepends=True)

    table_ours = _lcs_table(base_lines, ours_lines)
    hunks_ours = _extract_hunks(base_lines, ours_lines, table_ours)

    table_theirs = _lcs_table(base_lines, theirs_lines)
    hunks_theirs = _extract_hunks(base_lines, theirs_lines, table_theirs)

    merged_lines, has_conflicts = _merge_hunks(base_lines, hunks_ours, hunks_theirs)
    return "".join(merged_lines), has_conflicts
