# A8 TypeCheck -- Compiler Loop Assessment

## 1. Number of Compile Cycles

**10 compile cycles total** (cycles 1--10).

- Cycle 1: Initial compile of bare `_` hole.
- Cycle 2: Compile after introducing 6 named holes via pattern matching.
- Cycle 3: Compile after filling `_lit`.
- Cycle 4: Compile after filling `_bool`.
- Cycle 5: Compile after filling `_var`.
- Cycle 6: Compile after filling `_abs`.
- Cycle 7: Compile after filling `_app` partially (introducing `_appCheck` sub-hole).
- Cycle 8: Compile after filling `_appCheck`.
- Cycle 9: Compile after filling `_if` partially (introducing `_ifCheck` sub-hole).
- Cycle 10: Compile after filling `_ifCheck`. **Success.**

## 2. Holes Introduced and Filled

| Hole | Introduced | Filled | Fill Value |
|------|-----------|--------|------------|
| `_` (bare) | Initial | Cycle 1 | Replaced with 6-way pattern match + named holes |
| `_lit` | Cycle 1 | Cycle 2 | `Right TInt` |
| `_bool` | Cycle 1 | Cycle 3 | `Right TBool` |
| `_var` | Cycle 1 | Cycle 4 | `case lookup x env of Just ty -> Right ty; Nothing -> Left ...` |
| `_abs` | Cycle 1 | Cycle 5 | `do bodyTy <- typeCheck ((x,ty):env) body; Right (TFun ty bodyTy)` |
| `_app` | Cycle 1 | Cycle 6 | `do funTy <- ...; argTy <- ...; _appCheck` (partial, introduced sub-hole) |
| `_appCheck` | Cycle 6 | Cycle 7 | `case funTy of TFun paramTy resTy | argTy == paramTy -> Right resTy ...` |
| `_if` | Cycle 1 | Cycle 8 | `do condTy <- ...; ty1 <- ...; ty2 <- ...; _ifCheck` (partial, introduced sub-hole) |
| `_ifCheck` | Cycle 8 | Cycle 9 | `if condTy /= TBool then Left ... else if ty1 /= ty2 then Left ... else Right ty1` |

**Total: 9 holes introduced, 9 holes filled** (including 2 sub-holes for the complex cases).

## 3. Fill Order and Constraint Reasoning

The fill order was determined by choosing the most constrained hole at each step:

1. **`_` -> pattern match**: Only one valid structural step -- introduce case analysis on Term constructors. The type `Env -> Term -> Either String Type` demands pattern matching.

2. **`_lit` first**: Most constrained -- bindings are `_n :: Int`, `env :: Env`. No subterms to recurse on. Exactly one valid fill: `Right TInt`.

3. **`_bool` second**: Equally constrained to `_lit` -- bindings are `_b :: Bool`, `env :: Env`. Exactly one valid fill: `Right TBool`.

4. **`_var` third**: Next most constrained -- bindings are `x :: String`, `env :: Env`. The `lookup` function is the only way to produce `Either String Type` from `String` and `[(String, Type)]`.

5. **`_abs` fourth**: More constrained than `_app` and `_if` because it has `ty :: Type` already available as a binding. The fill pattern is straightforward: extend env, recurse on body, wrap with `TFun`.

6. **`_app` fifth (with sub-hole)**: Complex case requiring two recursive calls plus type matching. Split into: recursive calls (straightforward `do` bindings) + `_appCheck` sub-hole (the interesting logic). This decomposition was guided by the principle of filling what is known and leaving the unknown as a hole.

7. **`_appCheck`**: After cycle 7, diagnostics showed `funTy :: Type` and `argTy :: Type` in scope, making the case analysis on `TFun` the only viable structure.

8. **`_if` sixth (with sub-hole)**: Similar decomposition to `_app`. Three recursive calls are mechanical; the constraint logic (`_ifCheck`) was deferred.

9. **`_ifCheck`**: Diagnostics showed `condTy :: Type`, `ty1 :: Type`, `ty2 :: Type` in scope. The guards (condTy must be TBool, branches must match) follow directly from the type checker's invariants.

**Constraint ordering rationale**: Leaf cases (TmLit, TmBool) have exactly one fit. TmVar has a simple lookup pattern. TmAbs extends env and recurses once. TmApp and TmIf require multiple recursive calls plus constraint checking, so they were deferred and decomposed via sub-holes.

## 4. Total Tool Calls

| Tool | Count |
|------|-------|
| Read | 2 (initial file + final verification) |
| Edit | 9 (1 pattern match expansion + 6 hole fills + 2 sub-hole fills) |
| Bash (compile) | 10 |
| **Total** | **21** |
