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
    # Backtrack through LCS table to get list of matched pairs (base_idx, other_idx)
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

    Walk through the base lines. At each position, check if either (or both)
    sides have a hunk starting at or covering this position.

    - Non-overlapping hunk from one side: apply it.
    - Overlapping hunks with identical replacement: apply once (no conflict).
    - Overlapping hunks with different replacements: emit conflict markers.
    - No hunk: emit the base line.

    Returns (merged_lines, has_conflicts).
    """
    output: List[str] = []
    has_conflicts = False
    base_pos = 0
    oi = 0  # index into hunks_ours
    ti = 0  # index into hunks_theirs

    while base_pos <= len(base) or oi < len(hunks_ours) or ti < len(hunks_theirs):
        # Find next hunk start from each side (or sentinel past end)
        o_start = hunks_ours[oi].base_start if oi < len(hunks_ours) else len(base) + 1
        t_start = hunks_theirs[ti].base_start if ti < len(hunks_theirs) else len(base) + 1

        # Next event position
        next_event = min(o_start, t_start)

        # If no more events, emit remaining base lines and stop
        if next_event > len(base):
            output.extend(base[base_pos:])
            break

        # Emit unchanged base lines up to the next event
        output.extend(base[base_pos:next_event])
        base_pos = next_event

        # Determine which hunks are active at this position
        ho = hunks_ours[oi] if oi < len(hunks_ours) and hunks_ours[oi].base_start == base_pos else None
        ht = hunks_theirs[ti] if ti < len(hunks_theirs) and hunks_theirs[ti].base_start == base_pos else None

        # Check for overlap: one side starts inside the other's base range
        if ho and not ht and ti < len(hunks_theirs):
            ht_next = hunks_theirs[ti]
            if ht_next.base_start < ho.base_end:
                ht = ht_next
        if ht and not ho and oi < len(hunks_ours):
            ho_next = hunks_ours[oi]
            if ho_next.base_start < ht.base_end:
                ho = ho_next

        if ho and ht:
            # Both sides have changes in overlapping region
            # Check for identical changes (same base range and same replacement)
            if ho.base_start == ht.base_start and ho.base_end == ht.base_end and ho.other_lines == ht.other_lines:
                # Identical change — apply once, no conflict
                output.extend(ho.other_lines)
                base_pos = ho.base_end
            else:
                # Conflict: compute the union base range
                conflict_start = min(ho.base_start, ht.base_start)
                conflict_end = max(ho.base_end, ht.base_end)
                # Collect all ours/theirs hunks that fall within the conflict region
                ours_lines: List[str] = []
                theirs_lines: List[str] = []
                # Walk ours hunks overlapping the conflict region
                o_pos = conflict_start
                temp_oi = oi
                while temp_oi < len(hunks_ours) and hunks_ours[temp_oi].base_start < conflict_end:
                    h = hunks_ours[temp_oi]
                    ours_lines.extend(base[o_pos:h.base_start])
                    ours_lines.extend(h.other_lines)
                    o_pos = h.base_end
                    temp_oi += 1
                ours_lines.extend(base[o_pos:conflict_end])
                # Walk theirs hunks overlapping the conflict region
                t_pos = conflict_start
                temp_ti = ti
                while temp_ti < len(hunks_theirs) and hunks_theirs[temp_ti].base_start < conflict_end:
                    h = hunks_theirs[temp_ti]
                    theirs_lines.extend(base[t_pos:h.base_start])
                    theirs_lines.extend(h.other_lines)
                    t_pos = h.base_end
                    temp_ti += 1
                theirs_lines.extend(base[t_pos:conflict_end])

                # Check if the reconstructed sides are actually the same
                if ours_lines == theirs_lines:
                    output.extend(ours_lines)
                else:
                    has_conflicts = True
                    # Ensure conflict markers are on their own lines
                    if ours_lines and ours_lines[-1] and not ours_lines[-1].endswith("\n"):
                        ours_lines[-1] += "\n"
                    if theirs_lines and theirs_lines[-1] and not theirs_lines[-1].endswith("\n"):
                        theirs_lines[-1] += "\n"
                    output.append("<<<<<<< OURS\n")
                    output.extend(ours_lines)
                    output.append("=======\n")
                    output.extend(theirs_lines)
                    output.append(">>>>>>> THEIRS\n")

                base_pos = conflict_end
                # Advance hunk indices past the conflict region
                while oi < len(hunks_ours) and hunks_ours[oi].base_start < conflict_end:
                    oi += 1
                while ti < len(hunks_theirs) and hunks_theirs[ti].base_start < conflict_end:
                    ti += 1
                continue

            oi += 1
            ti += 1

        elif ho:
            # Only ours changed this region
            output.extend(ho.other_lines)
            base_pos = ho.base_end
            oi += 1

        elif ht:
            # Only theirs changed this region
            output.extend(ht.other_lines)
            base_pos = ht.base_end
            ti += 1

        else:
            # No hunk at this position — emit one base line and advance
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
