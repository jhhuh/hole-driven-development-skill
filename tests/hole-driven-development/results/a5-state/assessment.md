# A5-State: Hole-Driven Development Assessment

## Final Code

```haskell
module Stack where

import Control.Monad.State

type Stack = [Int]

push :: Int -> State Stack ()
push x = modify (x:)

pop :: State Stack Int
pop = do
  s <- get
  let (x:xs) = s
  put xs
  return x

evalRPN :: [String] -> State Stack ()
evalRPN = mapM_ step
  where
    step "+" = do a <- pop; b <- pop; push (b + a)
    step "-" = do a <- pop; b <- pop; push (b - a)
    step "*" = do a <- pop; b <- pop; push (b * a)
    step n   = push (read n)
```

## 1. Number of Compile Cycles

**12 compile cycles total** (including the final successful one).

| Cycle | Action | Result |
|-------|--------|--------|
| 1 | Rename bare `_` to named holes `_push`, `_pop`, `_evalRPN` | 3 hole diagnostics |
| 2 | Fill `_push` with `modify (x:)` | Compiled; 2 holes remain |
| 3 | Decompose `_pop` into `_popGet`, `_popPut`, `_popReturn` sub-holes | MonadFail error + 3 sub-hole diagnostics |
| 4 | Fill `_popGet` with `get`, fix failable pattern to `let` binding | 2 sub-holes remain + `_evalRPN` |
| 5 | Fill `_popPut` with `put xs` | 1 sub-hole remains + `_evalRPN` |
| 6 | Fill `_popReturn` with `return x` | Only `_evalRPN` remains |
| 7 | Decompose `_evalRPN` into `mapM_ _step` | `_step :: String -> State Stack b0` |
| 8 | Decompose `_step` into `step` with 4 case sub-holes | 4 sub-hole diagnostics |
| 9 | Fill `_stepNum` with `push (read n)` | 3 operator holes remain; type resolves to `State Stack ()` |
| 10 | Fill `_stepAdd` with `do a <- pop; b <- pop; push (b + a)` | 2 holes remain |
| 11 | Fill `_stepSub` with `do a <- pop; b <- pop; push (b - a)` | 1 hole remains |
| 12 | Fill `_stepMul` with `do a <- pop; b <- pop; push (b * a)` | SUCCESS |

## 2. Holes Introduced and Filled

### Original holes (3)
- `_push :: State Stack ()` -- filled cycle 2
- `_pop :: State Stack Int` -- decomposed cycle 3
- `_evalRPN :: [String] -> State Stack ()` -- decomposed cycle 7

### Sub-holes introduced by decomposition (7)
- `_popGet` -- filled cycle 4 with `get`
- `_popPut` -- filled cycle 5 with `put xs`
- `_popReturn` -- filled cycle 6 with `return x`
- `_step` -- decomposed cycle 8 into 4 case branches
- `_stepAdd` -- filled cycle 10
- `_stepSub` -- filled cycle 11
- `_stepMul` -- filled cycle 12
- `_stepNum` -- filled cycle 9

**Total holes introduced: 11** (3 original + 8 sub-holes from decomposition)
**Total holes filled with final code: 8** (3 decomposition holes became structure, 8 became terminal fills)

## 3. Fill Order and Reasoning

1. **`_push` first** -- Most constrained of the original 3. Type `State Stack ()` with `x :: Int` in scope. Only sensible fill: `modify (x:)`. No sub-holes needed.

2. **`_pop` second** -- Next most constrained. Required decomposition into `get`/destructure/`put`/`return` pattern. Filled sub-holes in data-flow order:
   - `_popGet` -> `get` (compiler suggested it as valid hole fit)
   - Fixed MonadFail issue by switching from failable `<-` pattern to `let` binding
   - `_popPut` -> `put xs` (xs in scope from let binding, need to update state)
   - `_popReturn` -> `return x` (x in scope, return type is `State Stack Int`)

3. **`_evalRPN` last** -- Most complex, depends on `push`/`pop`. Decomposed in two stages:
   - First into `mapM_ _step` (structural: iterate over token list)
   - Then `_step` into 4 case branches
   - Filled `_stepNum` first because it resolves the ambiguous type variable `p` to `State Stack ()`, giving the compiler concrete type information for the remaining holes
   - Then filled operator cases in order: `_stepAdd`, `_stepSub`, `_stepMul`

**Key compiler-driven decisions:**
- Cycle 3: The compiler's `MonadFail` error forced restructuring from `(x:xs) <- get` to `s <- get; let (x:xs) = s`
- Cycle 4: The compiler listed `get` as a valid hole fit for `_popGet`, confirming the correct fill
- Cycle 9: Filling `_stepNum` first caused the inferred type `p` to resolve to `State Stack ()`, which the compiler then used for the remaining operator holes

## 4. Total Tool Calls

| Tool | Count | Purpose |
|------|-------|---------|
| Read | 2 | Read initial file + verify final file |
| Edit | 10 | 1 rename to named holes + 9 hole fills |
| Bash (ghc compile) | 10 | 10 compilation checks (cycles 1-12, some edits share cycles) |
| Write | 1 | Write this assessment |
| **Total** | **23** | |
