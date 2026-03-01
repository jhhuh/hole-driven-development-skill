# B7 REST API -- HDD Assessment

## 1. Number of Holes Across All Files

**15 holes total** across 4 files:

| File         | Holes | IDs        |
|-------------|-------|------------|
| models.py   | 2     | HOLE_1, HOLE_2 |
| storage.py  | 6     | HOLE_3 -- HOLE_8 |
| handlers.py | 5     | HOLE_9 -- HOLE_13 |
| main.py     | 2     | HOLE_14, HOLE_15 |

## 2. Fill Order with Reasoning

### Phase 2: Interface-defining holes (most constrained first)

1. **HOLE_1** (Bookmark dataclass) -- Most constrained. Every other file depends on this type's shape. Zero dependencies of its own.
2. **HOLE_2** (Bookmark.to_dict) -- Depends on HOLE_1's fields. Needed by handlers to serialize responses.
3. **HOLE_3** (Storage data structure) -- Depends on Bookmark type. Defines the internal representation that all CRUD methods operate on.

### Phase 3: Implementation holes (dependency order)

4. **HOLE_4** (storage.create) -- First CRUD method. Exercises both the data structure and id counter from HOLE_3.
5. **HOLE_5** (storage.get) -- Simple lookup. Needed by handle_get.
6. **HOLE_6** (storage.list_all) -- Simple iteration. Needed by handle_list.
7. **HOLE_7** (storage.update) -- Partial update logic. Needed by handle_update.
8. **HOLE_8** (storage.delete) -- Removal logic. Needed by handle_delete.
9. **HOLE_9** (handle_create) -- First handler. Depends on storage.create + Bookmark.to_dict.
10. **HOLE_10** (handle_get) -- Depends on storage.get.
11. **HOLE_11** (handle_list) -- Depends on storage.list_all.
12. **HOLE_12** (handle_update) -- Depends on storage.update.
13. **HOLE_13** (handle_delete) -- Depends on storage.delete.
14. **HOLE_14** (request routing) -- Depends on all handlers. Parses HTTP path/method and dispatches.
15. **HOLE_15** (server setup) -- Depends on the handler class being complete. Least constrained (pure wiring).

**Principle applied**: Fill the most constrained holes first (those with the most dependents and fewest dependencies). This means types before storage, storage before handlers, handlers before routing/server.

## 3. Cross-File Dependency Handling

The dependency graph across files is:

```
models.py  <--  storage.py  <--  handlers.py  <--  main.py
```

This is a strict linear dependency chain, which made the fill order straightforward:

- **models.py** was filled first because it defines the `Bookmark` type used everywhere. Both `storage.py` (imports `Bookmark`) and `handlers.py` (calls `.to_dict()`) depend on it.
- **storage.py** was filled next. Its class interface (method signatures) was defined during Phase 1 skeleton creation, so handlers could be written against those contracts even before storage internals were filled. However, filling storage internals first ensured the contracts were validated.
- **handlers.py** functions depend on `BookmarkStorage` methods. The request/response contract (`request: dict -> (status, dict)`) was defined in the skeleton phase, allowing `main.py`'s routing to be written against handler signatures without knowing handler internals.
- **main.py** depends on both storage (instantiation) and handlers (dispatch). It was filled last since it is pure wiring with no business logic.

Key technique: **The skeleton phase defined all cross-file contracts (imports, method signatures, parameter shapes) upfront.** This meant each hole could be filled in isolation, confident that it would integrate correctly. The `request` dict shape (`{id, body}`) served as the implicit interface contract between `main.py` routing and `handlers.py` functions.

## 4. Total Tool Calls

**43 tool calls** total:

- 3 Bash calls (mkdir, directory setup)
- 4 Write calls (initial skeleton files + assessment)
- 15 Edit calls (one per hole + 1 cleanup of unused import)
- 6 Read calls (verify file state before/after edits)
- 2 Grep calls (count holes, verify zero remaining)
- 13 TaskCreate/TaskUpdate calls (progress tracking)
