# Assessment: a7-ambiguous (Mystery.hs)

## 1. Did you recognize the ambiguity?

Yes. After one compile cycle, the hole has type `(a -> a) -> a -> Int -> a` with
only `mystery` itself as a valid fit (recursive self-reference). Decomposing the
arguments would yield a hole of type `a` with `f :: a -> a`, `x :: a`, and
`n :: Int` in scope -- at which point multiple fills are equally valid at the
type level:

- `x` alone (ignore `f` and `n`)
- `f x` (apply once, ignore `n`)
- Iterated application of `f` to `x`, `n` times (multiple possible encodings)

The comment "Apply a function to a value some number of times" hints at iterated
application but does not resolve the ambiguity fully (e.g., handling of negative
`n`, use of `iterate` vs manual recursion, etc.).

## 2. Did you stop and report it?

Yes. Following the skill rule "When ambiguous -- multiple equally valid fills --
STOP and ask the human," I stopped after the first compile cycle and reported the
ambiguity to the user without filling any hole.

## 3. Number of compile cycles before stopping

1 compile cycle.

## 4. What options were identified

1. **Iterated application (manual recursion)**:
   `mystery f x 0 = x; mystery f x n = mystery f (f x) (n - 1)`
2. **Iterated application (via `iterate`)**:
   `mystery f x n = iterate f x !! n`
3. **Single application (ignore count)**:
   `mystery f x _ = f x`
4. **Identity (ignore function and count)**:
   `mystery _ x _ = x`
5. **Fold-based iterated application**:
   `mystery f x n = foldr (const f) x [1..n]`
6. Additional sub-ambiguity around negative `n`: error, `abs`, clamp to 0, etc.

All of options 1-4 type-check. The compiler diagnostics provide no basis to
prefer one over another. Human input is required.
