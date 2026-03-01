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
    """
    Compute a list of matching and changed blocks between base and other.

    Returns a list of (tag, base_start, base_end, other_start, other_end) tuples
    where tag is 'equal' or 'replace'. Ranges are half-open [start, end).

    This is similar to difflib.SequenceMatcher.get_opcodes() but uses pure LCS.
    """
    dp = _lcs_table(base, other)

    # Backtrack to find matching pairs (indices into base and other).
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

    # Convert matching pairs into opcodes (equal / replace blocks).
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
    """Merge consecutive equal blocks and consecutive replace blocks."""
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
    """Three-way merge. Returns (merged_text, has_conflicts)."""
    # Trivial short-circuits.
    if ours == theirs:
        return (ours, False)
    if base == ours:
        return (theirs, False)
    if base == theirs:
        return (ours, False)

    base_lines = base.splitlines(True)
    ours_lines = ours.splitlines(True)
    theirs_lines = theirs.splitlines(True)

    # Get change blocks for each side relative to base.
    ours_blocks = _collapse_equal(_compute_blocks(base_lines, ours_lines))
    theirs_blocks = _collapse_equal(_compute_blocks(base_lines, theirs_lines))

    # Build a map: for each base region, what did each side do?
    # We'll walk both block lists simultaneously, splitting on base-line boundaries
    # to align them.

    # Expand blocks into per-base-region change records.
    # A "change" is: base range [bs, be) was replaced with lines from other[os:oe).
    # For 'equal' blocks, the replacement is identical to base.

    # Strategy: walk through base line by line using two cursors into
    # ours_blocks and theirs_blocks. Group contiguous changed regions
    # from either side, then decide: apply, conflict, or pass through.

    # Convert blocks to a more convenient representation: a list of
    # (base_start, base_end, replacement_lines, is_change) for each side.
    def to_regions(blocks, other_lines):
        regions = []
        for tag, bs, be, os, oe in blocks:
            regions.append((bs, be, other_lines[os:oe], tag == 'replace'))
        return regions

    ours_regions = to_regions(ours_blocks, ours_lines)
    theirs_regions = to_regions(theirs_blocks, theirs_lines)

    # Now we need to walk both region lists and align them by base position.
    # When both sides have a change that overlaps the same base range, that's
    # a potential conflict.

    # Split regions so that every region boundary from one side is also a
    # boundary in the other side. This lets us compare them element-wise.

    def split_at(regions, base_lines, cut_points):
        """Split regions at the given base-line cut points."""
        result = []
        ri = 0
        for region in regions:
            bs, be, repl, changed = region
            # Collect cut points that fall strictly inside this region.
            cuts = [c for c in cut_points if bs < c < be]
            if not cuts:
                result.append(region)
                continue
            # Split an equal region at the cut points.
            if not changed:
                prev = bs
                for c in cuts:
                    result.append((prev, c, base_lines[prev:c], False))
                    prev = c
                result.append((prev, be, base_lines[prev:be], False))
            else:
                # For a changed region, we can't meaningfully split the
                # replacement text. The whole region is one atomic change.
                # Instead, we'll expand the corresponding region on the other
                # side to cover the same base range (handled at the merge level).
                result.append(region)
        return result

    # Gather all boundary points from both sides.
    def boundaries(regions):
        pts = set()
        for bs, be, _, _ in regions:
            pts.add(bs)
            pts.add(be)
        return pts

    all_cuts = sorted(boundaries(ours_regions) | boundaries(theirs_regions))
    ours_regions = split_at(ours_regions, base_lines, all_cuts)
    theirs_regions = split_at(theirs_regions, base_lines, all_cuts)

    # Now merge. We walk through the base using indices into both region lists.
    # At each step we find the next base span covered by the front of each list
    # and decide what to emit.

    output: list[str] = []
    has_conflicts = False

    oi, ti = 0, 0  # cursors into ours_regions, theirs_regions

    while oi < len(ours_regions) or ti < len(theirs_regions):
        # Determine which base range to handle next.
        if oi < len(ours_regions) and ti < len(theirs_regions):
            obs, obe = ours_regions[oi][0], ours_regions[oi][1]
            tbs, tbe = theirs_regions[ti][0], theirs_regions[ti][1]

            # If the regions cover the exact same base range, compare directly.
            if obs == tbs and obe == tbe:
                o_repl, o_changed = ours_regions[oi][2], ours_regions[oi][3]
                t_repl, t_changed = theirs_regions[ti][2], theirs_regions[ti][3]

                if not o_changed and not t_changed:
                    # Both unchanged: emit base.
                    output.extend(o_repl)
                elif o_changed and not t_changed:
                    # Only ours changed.
                    output.extend(o_repl)
                elif not o_changed and t_changed:
                    # Only theirs changed.
                    output.extend(t_repl)
                else:
                    # Both changed.
                    if o_repl == t_repl:
                        # Same change: no conflict.
                        output.extend(o_repl)
                    else:
                        # Conflict.
                        has_conflicts = True
                        output.append('<<<<<<< OURS\n')
                        output.extend(_ensure_newline(o_repl))
                        output.append('=======\n')
                        output.extend(_ensure_newline(t_repl))
                        output.append('>>>>>>> THEIRS\n')
                oi += 1
                ti += 1
                continue

            # Regions don't align perfectly. One side has a change spanning
            # a range that the other side has split into smaller pieces
            # (or vice versa). We need to collect all regions from both sides
            # that overlap and handle them together.

            # Determine the overlapping super-range.
            start = min(obs, tbs)
            end = max(obe, tbe)

            # But we want to be more precise: gather all contiguous regions
            # from both sides that overlap with each other, forming one
            # "conflict group" if any side has a change.
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
            # Only ours left (theirs exhausted).
            output.extend(ours_regions[oi][2])
            oi += 1
        else:
            # Only theirs left (ours exhausted).
            output.extend(theirs_regions[ti][2])
            ti += 1

    merged = ''.join(output)
    return (merged, has_conflicts)


def _collect_overlap_group(
    ours_regions, theirs_regions, oi, ti
) -> tuple[list, list, int, int]:
    """
    Starting from current cursors, collect all regions from both sides
    whose base ranges overlap, forming one contiguous group.
    Returns (ours_group, theirs_group, new_oi, new_ti).
    """
    o_group = []
    t_group = []

    # The group spans a base range. Start with the first region from each side.
    group_end = 0

    if oi < len(ours_regions):
        o_group.append(ours_regions[oi])
        group_end = max(group_end, ours_regions[oi][1])
        oi += 1
    if ti < len(theirs_regions):
        t_group.append(theirs_regions[ti])
        group_end = max(group_end, theirs_regions[ti][1])
        ti += 1

    # Extend group while the next region on either side starts before group_end.
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
    """Extract the replacement lines from a group of regions."""
    lines = []
    for _, _, repl, _ in group:
        lines.extend(repl)
    return lines


def _ensure_newline(lines: list[str]) -> list[str]:
    """Ensure the last line ends with a newline, for clean conflict markers."""
    if not lines:
        return lines
    if lines[-1] and not lines[-1].endswith('\n'):
        return lines[:-1] + [lines[-1] + '\n']
    return lines
