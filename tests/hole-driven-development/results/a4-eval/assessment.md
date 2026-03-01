# A4-eval: Compiler Loop Assessment

## Final Code

```haskell
eval :: Expr -> Int
eval (Lit n)   = n
eval (Add l r) = eval l + eval r
eval (Mul l r) = eval l * eval r
eval (Neg e)   = negate (eval e)
```

## 1. Number of Compile Cycles: 6

| Cycle | Action | Result |
|-------|--------|--------|
| 1 | Compile initial `_` hole | Diagnostic: `_ :: Expr -> Int` |
| 2 | Case-split into 4 named holes (`_lit`, `_add`, `_mul`, `_neg`) | 4 hole diagnostics with bindings |
| 3 | Fill `_lit` with `n` | 3 holes remain |
| 4 | Fill `_neg` with `negate (eval e)` | 2 holes remain |
| 5 | Fill `_add` with `eval l + eval r` | 1 hole remains |
| 6 | Fill `_mul` with `eval l * eval r` | Compilation succeeds |

## 2. Holes Introduced and Filled

| Hole | Introduced | Filled | Fill Value |
|------|-----------|--------|------------|
| `_` (anonymous) | Cycle 1 (initial) | Cycle 2 (replaced by case split) | Pattern match on 4 constructors |
| `_lit` | Cycle 2 | Cycle 3 | `n` |
| `_neg` | Cycle 2 | Cycle 4 | `negate (eval e)` |
| `_add` | Cycle 2 | Cycle 5 | `eval l + eval r` |
| `_mul` | Cycle 2 | Cycle 6 | `eval l * eval r` |

## 3. Fill Order and Constraint Reasoning

1. **`_` -> case split** (Cycle 2): The initial hole had type `Expr -> Int`. The only way to produce an `Int` from an `Expr` is to pattern match on all four constructors. This decomposition step introduced four sub-holes.

2. **`_lit` first** (Cycle 3): Most constrained. The compiler showed `n :: Int` as a valid hole fit directly. The hole needs `Int`, and `n` is the only `Int` in scope. No recursive calls needed -- uniquely determined.

3. **`_neg` second** (Cycle 4): Next most constrained. Only one sub-expression binding (`e :: Expr`), so there is only one recursive call to make (`eval e`). The result must be negated. Simpler than `_add`/`_mul` which each have two sub-expressions.

4. **`_add` third** (Cycle 5): Bindings `l :: Expr`, `r :: Expr`. Both must be recursively evaluated and combined with `(+)`. Structurally identical to `_mul`, so filled by top-down order.

5. **`_mul` last** (Cycle 6): Same structure as `_add` but with `(*)`. Last remaining hole.

**Constraint ordering principle**: Fill base cases before recursive cases, fewer-binding holes before more-binding holes, and break ties by source order.

## 4. Total Tool Calls

| Tool | Count |
|------|-------|
| Read | 2 |
| Edit | 5 |
| Bash (compile) | 6 |
| **Total** | **13** |
