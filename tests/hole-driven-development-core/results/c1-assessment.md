# c1-double: Self-Assessment

## 1. What I did

I skipped HDD decomposition and implemented `double` directly as `return x * 2`.

## 2. Why

The HDD skill explicitly lists a red flag:

> Creating artificial decomposition for trivial one-liners (1-2 lines of obvious code)

`double(x: int) -> int` has exactly one obvious, unambiguous implementation: `return x * 2`. There are no sub-problems to decompose into, no unknowns to leave as holes, and no ambiguity that would benefit from incremental filling. Introducing holes here would be pure ceremony with no decision-making value.

## 3. Tool calls / iterations

- 1 tool call to check the target directory exists
- 1 tool call to write the implementation
- 1 tool call to write this assessment
- Total: 3 tool calls, 0 HDD iterations (decomposition was not warranted)
