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
  - Both sides make the same change -> no conflict
  - One side deletes a line, other modifies it -> conflict
  - Both sides insert at the same point -> conflict
  - Empty files
  - One side unchanged -> take the other side's changes entirely
"""


def _lcs_opcodes(a: list[str], b: list[str]) -> list[tuple[str, int, int, int, int]]:
    """Compute LCS-based diff opcodes between sequences a and b.

    Returns list of (tag, a_start, a_end, b_start, b_end) where tag is
    'equal', 'replace', 'insert', or 'delete'.
    """
    # HOLE_1a filled: compute LCS table and backtrack to matching blocks
    m, n = len(a), len(b)
    # dp[i][j] = LCS length of a[:i], b[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to find individual LCS matches (i, j) pairs
    matches = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            matches.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    matches.reverse()

    # Collapse consecutive matches into blocks (a_idx, b_idx, length)
    blocks = []
    for ai, bj in matches:
        if blocks and blocks[-1][0] + blocks[-1][2] == ai and blocks[-1][1] + blocks[-1][2] == bj:
            blocks[-1] = (blocks[-1][0], blocks[-1][1], blocks[-1][2] + 1)
        else:
            blocks.append((ai, bj, 1))
    blocks.append((m, n, 0))  # sentinel

    # HOLE_1b filled: convert matching blocks to opcodes
    opcodes = []
    ai = bj = 0
    for (a_idx, b_idx, size) in blocks:
        # Gap before this matching block
        if ai < a_idx or bj < b_idx:
            if ai < a_idx and bj < b_idx:
                tag = "replace"
            elif ai < a_idx:
                tag = "delete"
            else:
                tag = "insert"
            opcodes.append((tag, ai, a_idx, bj, b_idx))
        # The matching block itself (skip sentinel with size==0)
        if size:
            opcodes.append(("equal", a_idx, a_idx + size, b_idx, b_idx + size))
        ai = a_idx + size
        bj = b_idx + size
    return opcodes


def merge3(base: str, ours: str, theirs: str) -> tuple[str, bool]:
    """Three-way merge. Returns (merged_text, has_conflicts)."""
    base_lines = base.splitlines(keepends=True)
    ours_lines = ours.splitlines(keepends=True)
    theirs_lines = theirs.splitlines(keepends=True)

    # Step 1: Compute diffs from base to each side
    ours_ops = _lcs_opcodes(base_lines, ours_lines)
    theirs_ops = _lcs_opcodes(base_lines, theirs_lines)

    # Step 2: HOLE_2 filled — extract change hunks from opcodes
    # Each hunk: (base_start, base_end, replacement_lines)
    def _extract_hunks(ops, side_lines):
        hunks = []
        for tag, a1, a2, b1, b2 in ops:
            if tag != "equal":
                hunks.append((a1, a2, side_lines[b1:b2]))
        return hunks

    ours_hunks = _extract_hunks(ours_ops, ours_lines)
    theirs_hunks = _extract_hunks(theirs_ops, theirs_lines)

    # Step 3: Merge the two sets of hunks, detecting conflicts
    # Walk base with cursors into both sorted hunk lists.
    result_lines = []
    has_conflicts = False
    base_pos = 0  # current position in base
    oi = ti = 0   # cursors into ours_hunks, theirs_hunks

    while base_pos <= len(base_lines) or oi < len(ours_hunks) or ti < len(theirs_hunks):
        # Find next hunk start from each side (or sentinel at end-of-base)
        o_start = ours_hunks[oi][0] if oi < len(ours_hunks) else len(base_lines)
        t_start = theirs_hunks[ti][0] if ti < len(theirs_hunks) else len(base_lines)
        next_hunk_start = min(o_start, t_start)

        # Emit unchanged base lines before the next hunk
        if base_pos < next_hunk_start:
            result_lines.extend(base_lines[base_pos:next_hunk_start])
            base_pos = next_hunk_start

        # If we've consumed everything, break
        if oi >= len(ours_hunks) and ti >= len(theirs_hunks):
            # Emit any remaining base lines
            if base_pos < len(base_lines):
                result_lines.extend(base_lines[base_pos:])
            break

        # HOLE_3a filled: determine overlap and handle cases
        # Get current hunks from each side (if they start at base_pos)
        o_hunk = ours_hunks[oi] if oi < len(ours_hunks) else None
        t_hunk = theirs_hunks[ti] if ti < len(theirs_hunks) else None

        # Check for overlap: two hunks overlap if their base ranges intersect.
        # For insertions (start==end), they overlap only if at the same point.
        def _hunks_overlap(h1, h2):
            if h1 is None or h2 is None:
                return False
            s1, e1, _ = h1
            s2, e2, _ = h2
            # For pure insertions (s==e), they overlap only at the same point
            if s1 == e1 and s2 == e2:
                return s1 == s2
            # Otherwise, standard interval overlap (strict, not adjacent)
            return s1 < e2 and s2 < e1

        if _hunks_overlap(o_hunk, t_hunk):
            # HOLE_3b filled: handle overlapping hunks
            o_start, o_end, o_repl = o_hunk
            t_start, t_end, t_repl = t_hunk
            region_start = min(o_start, t_start)
            region_end = max(o_end, t_end)

            # What each side produces for the combined region
            ours_view = (
                list(base_lines[region_start:o_start])
                + list(o_repl)
                + list(base_lines[o_end:region_end])
            )
            theirs_view = (
                list(base_lines[region_start:t_start])
                + list(t_repl)
                + list(base_lines[t_end:region_end])
            )

            if ours_view == theirs_view:
                # Same change on both sides — no conflict
                result_lines.extend(ours_view)
            else:
                # HOLE_3c filled: emit conflict markers
                has_conflicts = True
                result_lines.append("<<<<<<< OURS\n")
                result_lines.extend(ours_view)
                result_lines.append("=======\n")
                result_lines.extend(theirs_view)
                result_lines.append(">>>>>>> THEIRS\n")

            base_pos = region_end
            oi += 1
            ti += 1
        elif o_hunk is not None and (t_hunk is None or o_hunk[0] <= t_hunk[0]):
            # Only ours at this position (theirs starts later or absent)
            _, o_end, o_repl = o_hunk
            result_lines.extend(o_repl)
            base_pos = max(base_pos, o_end)
            oi += 1
        else:
            # Only theirs at this position
            _, t_end, t_repl = t_hunk
            result_lines.extend(t_repl)
            base_pos = max(base_pos, t_end)
            ti += 1

    merged_text = "".join(result_lines)
    return merged_text, has_conflicts
