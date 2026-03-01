# B3 TodoList — HDD Iterative Reasoning Assessment

## Number of Holes

**4 holes** in the initial skeleton:

| Hole | Function | Description |
|------|----------|-------------|
| HOLE_1 | `filterItems` | Filter items array by all/active/completed |
| HOLE_2 | `renderItem` | Render a single TodoItem as an `<li>` HTML string |
| HOLE_3 | `renderList` | Map renderItem over items, wrap in `<ul>` |
| HOLE_4 | `assembleHtml` | Wrap list in container div with count summary |

## Fill Order with Reasoning

### 1. HOLE_1 (filterItems) — most constrained

**Why first:** Pure data transformation with fully determined inputs (`TodoItem[]` + union type filter). The switch on `'all' | 'active' | 'completed'` has exactly one correct implementation per case. No dependencies on other holes.

**Contract:** `(items: TodoItem[], filter: 'all' | 'active' | 'completed') => TodoItem[]`

### 2. HOLE_2 (renderItem) — next most constrained

**Why second:** Single-item rendering with clear inputs (one `TodoItem`). The output structure is largely determined by the fields available: `id`, `text`, `completed`. No dependency on other unfilled holes. Must be filled before HOLE_3 (which calls it).

**Contract:** `(item: TodoItem) => string` (an `<li>` element)

### 3. HOLE_3 (renderList) — unblocked after HOLE_2

**Why third:** Trivially constrained once `renderItem` exists — just `map` + `join` + wrap in `<ul>`. Only one reasonable implementation.

**Contract:** `(items: TodoItem[]) => string` (a `<ul>` element)

### 4. HOLE_4 (assembleHtml) — least constrained

**Why last:** The outer wrapper has the most design freedom (many valid HTML structures). Filling it last means all inner content is already determined, making the wrapping decision straightforward.

**Contract:** `(listHtml: string, visibleCount: number, totalCount: number) => string`

## Total Tool Calls

**15 tool calls** (excluding task-tracking meta-calls):

- 5 exploratory (ls, glob, read skill files)
- 1 mkdir
- 1 write (skeleton)
- 2 read (file state before edits + final verification)
- 4 edit (one per hole fill)
- 2 additional (glob for skills directory, ls for b3 directory)
