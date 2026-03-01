# B6 Backup Rotation - HDD Iterative Reasoning Assessment

## 1. Number of Holes

**5 holes** -- one per pipeline stage:

| Hole   | Concern                | Contract (informal)                                                 |
|--------|------------------------|---------------------------------------------------------------------|
| HOLE_1 | Validate input         | `$1` must be non-empty and an existing directory, else error+exit   |
| HOLE_2 | List backup files      | Glob `backup-YYYY-MM-DD.tar.gz` into array; early-return if empty   |
| HOLE_3 | Compute age boundaries | Set epoch cutoffs: 7 days, 28 days, 365 days before now             |
| HOLE_4 | Classify & select      | For each file: extract date, assign to daily/weekly/monthly/discard |
| HOLE_5 | Delete non-kept files  | Iterate all files; rm those not in keep-set; report results         |

## 2. Fill Order with Reasoning

**Order: HOLE_1 -> HOLE_2 -> HOLE_3 -> HOLE_4 -> HOLE_5**

This follows sequential file order, which coincides with dependency order:

1. **HOLE_1 (validate input)** -- Most constrained. No dependencies. Guards all subsequent code. Without it, every other hole operates on potentially invalid state (missing or non-directory path).

2. **HOLE_2 (list files)** -- Depends only on HOLE_1 (valid directory). Produces the `backup_files` array consumed by HOLE_4 and HOLE_5. Must be filled before HOLE_3 because bash executes sequentially -- an unfilled HOLE_2 (`exit 1`) prevents HOLE_3 from ever running.

3. **HOLE_3 (compute boundaries)** -- Depends on HOLE_1 passing (implicit). Produces `cutoff_daily`, `cutoff_weekly`, `cutoff_monthly` -- the epoch thresholds that HOLE_4's classification logic requires. Pure computation with no file I/O.

4. **HOLE_4 (classify & select)** -- Depends on HOLE_2 (`backup_files` array) and HOLE_3 (cutoff values). The core logic: iterates files in reverse chronological order, extracts dates from filenames, assigns each file to a retention tier using associative-array deduplication (`seen_weeks`, `seen_months`). Produces the `keep_files` associative array.

5. **HOLE_5 (delete)** -- Depends on HOLE_2 (`backup_files` for iteration) and HOLE_4 (`keep_files` for the keep/delete decision). Least constrained -- purely mechanical once the keep-set is known.

**Note on bash-specific ordering constraint:** Unlike typed languages where holes can be filled in any order and the compiler checks consistency, bash holes must be filled in sequential file order because `echo ... && exit 1` terminates the script. An unfilled hole blocks all subsequent holes from executing during testing. This forced the fill order to match the textual order, which luckily also matched the dependency order here.

## 3. How HDD Worked for a Completely Untyped Language

### What worked well

- **Hole markers as executable guards.** The `echo "HOLE_N: ..." && exit 1` pattern serves as both documentation and a runtime assertion. When running the script, the output explicitly names which hole was hit, providing the same "where am I stuck?" feedback that a type error gives in typed languages.

- **Incremental testability.** After each hole fill, the script could be run and would either proceed to the next hole (success) or crash at the current hole (still unfilled). This created a natural red-green cycle: unfilled hole = red, filled hole = green (proceeds to next hole).

- **Contracts as comments.** Without types, the "contract" for each hole was expressed as English comments describing inputs, outputs, and invariants. For example, HOLE_4's contract specified that it reads `backup_files` (array from HOLE_2) and `cutoff_*` (integers from HOLE_3) and produces `keep_files` (associative array). This made the data flow explicit despite the absence of type signatures.

- **Decomposition forced clear boundaries.** Even in bash where global mutable state is the norm, the hole discipline forced each concern into a distinct section with named intermediate variables (`backup_files`, `cutoff_daily`, `keep_files`). This is better structure than typical bash scripts achieve.

### What was harder without types

- **No static verification of variable names.** A typo in `keep_files` vs `keep_file` would silently produce an empty variable. The only defense was careful manual review and runtime testing. In a typed language, the compiler catches this instantly.

- **No contract enforcement.** HOLE_4 could silently produce the wrong data structure (e.g., a regular variable instead of an associative array) and HOLE_5 would break at runtime with an unhelpful error. Typed holes guarantee interface compatibility at fill time.

- **`exit 1` is destructive.** The hole marker kills the entire script, not just the function. This meant I had to use `exit 1` (not `return 1`) to ensure the hole actually stopped execution when called via `backup_rotate "$1"`. In a typed language, an unfilled hole is a compile-time concept -- it never executes.

- **Bash-sequential ordering constraint.** Because holes execute at runtime, an unfilled hole blocks testing of all subsequent holes. In typed languages, you can fill holes in any order because the compiler evaluates all of them. This forced a strictly sequential fill order in bash.

### Verdict

HDD is viable in bash but the "oracle" shifts from the compiler to the developer's manual reasoning + runtime testing. The hole markers provide structure and incremental testability, but without a type checker, there is no static guarantee that filled holes produce values compatible with downstream consumers. The discipline compensates by making data flow explicit through named variables and commented contracts.

## 4. Total Tool Calls

| Tool   | Count | Purpose                                                  |
|--------|-------|----------------------------------------------------------|
| Glob   | 2     | Explore skill files and existing results                 |
| Read   | 7     | Prior assessments (2), file state before each edit (5)   |
| Write  | 2     | Initial skeleton, this assessment                        |
| Edit   | 5     | Fill HOLE_1 through HOLE_5                               |
| Bash   | 12    | mkdir (1), syntax checks (6), runtime tests (5)          |

**Total: 28 tool calls** (not counting this Write)
