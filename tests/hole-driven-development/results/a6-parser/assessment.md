# A6 Parser -- Compiler Loop Assessment

## 1. Number of Compile Cycles: 7

| Cycle | Action | Holes remaining after |
|-------|--------|-----------------------|
| 1 | Named all three initial holes (`_parseExpr`, `_parseTerm`, `_parseFactor`) | 3 |
| 2 | Split `_parseFactor` into pattern-match cases, introducing `_factorParen` and `_factorNum` | 4 (`_parseExpr`, `_parseTerm`, `_factorParen`, `_factorNum`) |
| 3 | Filled `_factorNum` with `span isDigit` + `Num (read digits)` | 3 (`_parseExpr`, `_parseTerm`, `_factorParen`) |
| 4 | Filled `_factorParen` with `case parseExpr rest of Just (e, ')':rest') -> ...` | 2 (`_parseExpr`, `_parseTerm`) |
| 5 | Partially filled `_parseTerm`: parsed first factor, introduced `_termLoop` | 2 (`_parseExpr`, `_termLoop`) |
| 6 | Filled `_termLoop` with left-associative `*`/`/` loop via `where` clause | 1 (`_parseExpr`) |
| 7 | Filled `_parseExpr` with same pattern as `parseTerm` but using `+`/`-` operators | 0 -- compilation succeeds |

## 2. Holes Introduced and Filled

| Hole | Type (from diagnostics) | Filled with |
|------|------------------------|-------------|
| `_parseExpr` | `String -> Maybe (Expr, String)` | `parseTerm` then left-associative `exprLoop` on `+`/`-` |
| `_parseTerm` | `String -> Maybe (Expr, String)` | `parseFactor` then left-associative `termLoop` on `*`/`/` |
| `_parseFactor` | `String -> Maybe (Expr, String)` | Pattern match on `'('` vs digit vs other |
| `_factorParen` | `[Char] -> Maybe (Expr, String)` | `case parseExpr rest of Just (e, ')':rest') -> Just (e, rest')` |
| `_factorNum` | `String -> Maybe (Expr, String)` | `span isDigit` + `Num (read digits)` |
| `_termLoop` | `Expr -> String -> Maybe (Expr, String)` | Guard on `*`/`/`, recurse with `BinOp`; base case returns accumulated expr |

Total: 6 holes introduced, 6 holes filled.

## 3. Mutual Recursion Handling

The grammar has mutual recursion: `expr -> term -> factor -> '(' expr ')'`.

Strategy: **Bottom-up with forward reference.**

1. Started with `parseFactor` (leaf parser, most constrained).
2. In the parenthesized-expression case (`_factorParen`), the compiler showed `parseExpr` as a valid hole fit of type `String -> Maybe (Expr, String)`. I used it as a forward reference -- calling `parseExpr` before its body was filled. GHC accepts this because Haskell bindings are mutually recursive by default at module scope.
3. Then filled `parseTerm` (depends on `parseFactor`, already complete).
4. Finally filled `parseExpr` (depends on `parseTerm`, already complete).

The mutual recursion resolved naturally: `parseFactor` calls `parseExpr` (which was still a hole at that point), and `parseExpr` calls `parseTerm` which calls `parseFactor`. GHC's lazy binding semantics made this work without any special annotation -- all three functions are in the same module, so they can reference each other regardless of definition order.

The compiler diagnostics were key: when filling `_factorParen`, GHC listed `parseExpr`, `parseTerm`, and `parseFactor` as valid fits. The type `[Char] -> Maybe (Expr, String)` matched all three, but the grammar dictated that `parseExpr` was the correct choice (parenthesized expressions contain full expressions, not just terms or factors).

## 4. Total Tool Calls

| Tool | Count | Purpose |
|------|-------|---------|
| Read | 2 | Read initial file, verify final file |
| Write | 1 | Initial named-hole setup (Edit failed on underscore matching) |
| Edit | 5 | Fill holes across cycles 2-7 |
| Bash (compile) | 7 | One per compile cycle |
| Bash (smoke test) | 1 | Verify correctness with sample expressions |
| **Total** | **16** | |
