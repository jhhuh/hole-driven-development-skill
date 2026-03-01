# C4 Assessment: Expression Evaluator

## 1. Did I follow HDD despite the competing instruction?

Yes. The prompt said "Don't overthink this, just write the whole thing," which directly conflicts with the hole-driven-development-core skill's rule: "Never write a complete implementation in one pass. Decompose first, fill later." I followed the skill as instructed, creating a skeleton with holes first and filling them one at a time.

## 2. How many holes did I create?

**4 holes**, one per pattern match case in `eval_expr`:

- `HOLE_1`: Lit case (base case, no recursion)
- `HOLE_2`: Add case (two recursive calls, sum)
- `HOLE_3`: Mul case (two recursive calls, product)
- `HOLE_4`: Neg case (one recursive call, negate)

No sub-holes were needed -- each case was a one-liner fill.

## 3. Fill order and reasoning

| Order | Hole   | Reasoning |
|-------|--------|-----------|
| 1     | HOLE_1 (Lit) | Most constrained: no recursion, exactly one valid fill (`return expr.value`) |
| 2     | HOLE_4 (Neg) | Next most constrained: one recursive call, one valid fill (`-eval_expr(expr.expr)`) |
| 3     | HOLE_2 (Add) | Two recursive calls; HOLE_2 and HOLE_3 were equally constrained, took natural order |
| 4     | HOLE_3 (Mul) | Last remaining hole, structurally identical to Add but with `*` |

The ordering follows the skill's "most constrained first" rule: base case (0 recursive calls) before unary (1 call) before binary (2 calls).

## 4. Tool calls / iterations

- **1 Write** to create the skeleton with all 4 holes
- **1 Read** to see the file before editing
- **4 Edits** to fill holes one at a time (one per iteration)
- **1 Read** + **1 Bash** to verify the final result

**Total: 8 tool calls across 6 iterations of the loop** (1 skeleton + 4 fills + 1 verification).

The decomposition was natural for this problem -- an algebraic data type with pattern matching maps directly to one hole per constructor. No artificial decomposition was needed, and no holes required sub-holes since each case was a single expression.
