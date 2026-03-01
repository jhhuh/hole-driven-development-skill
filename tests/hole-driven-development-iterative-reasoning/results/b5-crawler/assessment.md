# B5 Crawler - HDD Iterative Reasoning Assessment

## 1. Number of Holes

**5 holes** were identified in the skeleton:

| Hole   | Description                              | Type               |
|--------|------------------------------------------|---------------------|
| HOLE_1 | Build and load RobotFileParser for origin | Infrastructure      |
| HOLE_2 | Fetch URL, check content-type            | I/O + filtering     |
| HOLE_3 | Parse `<a>` tags, resolve relative hrefs | Parsing             |
| HOLE_4 | Cached robots.txt permission check       | Caching + delegation|
| HOLE_5 | BFS crawl loop with depth tracking       | Orchestration       |

## 2. Fill Order with Reasoning

**Order: HOLE_1 -> HOLE_2 -> HOLE_3 -> HOLE_4 -> HOLE_5**

The fill order follows a dependency-driven strategy (most constrained / least dependent first):

1. **HOLE_1 (robot checker factory)** -- Leaf function with no dependencies on other holes. Required by HOLE_4 to create checkers. Filled first because it is the deepest leaf in the call graph.

2. **HOLE_2 (fetch page)** -- Leaf function with no dependencies on other holes. Required by HOLE_5. Independent of HOLE_1, but placed second because HOLE_1 is depended upon by another hole (HOLE_4), making HOLE_1 slightly more constrained. User-Agent string established here ("crawl_links/1.0") becomes a cross-cutting contract that HOLE_4 must match.

3. **HOLE_3 (parse links)** -- Leaf function with no dependencies on other holes. Required by HOLE_5. Uses `HTMLParser` subclass internally. Produces `list[str]` of absolute http/https URLs. Independent of HOLE_1 and HOLE_2.

4. **HOLE_4 (is_allowed)** -- Depends on HOLE_1 (`_make_robot_checker`). Must use the same user-agent string as HOLE_2 ("crawl_links/1.0") for robots.txt semantics to be consistent. Adds caching layer via `robot_cache` dict passed by caller. Cannot be filled before HOLE_1.

5. **HOLE_5 (crawl loop)** -- Most dependent hole. Calls HOLE_2 (`_fetch_page`), HOLE_3 (`_parse_links`), and HOLE_4 (`_is_allowed`). Owns the BFS queue, visited set, result dict, and robot_cache. Filled last because it orchestrates all other components.

## 3. How the Lack of Type Checker Was Handled

Without a type checker, I served as the sole type oracle by:

- **Annotating each hole marker** with its expected return type in the `# expects:` comment (e.g., `# expects: RobotFileParser`, `# expects: str | None`, `# expects: list[str]`, `# expects: bool`, `# expects: dict[str, list[str]]`).

- **Reasoning about contracts at each boundary** before filling. For each hole I stated: what it receives (parameter types and semantics), what it produces (return type), what invariants it must uphold (e.g., user-agent consistency between HOLE_2 and HOLE_4).

- **Tracking cross-cutting contracts manually**. The user-agent string "crawl_links/1.0" appears in both `_fetch_page` (HOLE_2) and `_is_allowed` (HOLE_4). Without a type checker, this consistency was maintained through explicit reasoning during the fill of HOLE_4, noting it must match HOLE_2's value.

- **Verifying composition correctness** when filling HOLE_5: confirmed that `_fetch_page` returns `str | None` (checked before calling `_parse_links`), `_parse_links` returns `list[str]` (stored directly in `result`), and `_is_allowed` returns `bool` (used in conditional). The `robot_cache` dict is created in HOLE_5 and passed mutably to HOLE_4 -- this ownership pattern was verified manually.

- **Syntax validation** via `ast.parse()` as a final sanity check since no type checker was available.

## 4. Total Tool Calls

| Tool       | Count | Purpose                                          |
|------------|-------|--------------------------------------------------|
| Bash       | 4     | ls (2x), mkdir, nix-shell ast.parse              |
| Glob       | 2     | skills/*.md, scenario/assessment *.md             |
| Read       | 7     | scenario.md, b4 assessment, file state (5x)      |
| Write      | 2     | Initial skeleton, this assessment                 |
| Edit       | 6     | Fill HOLE_1, HOLE_2, HOLE_3, HOLE_4, HOLE_5, add import |

**Total: 21 tool calls**
