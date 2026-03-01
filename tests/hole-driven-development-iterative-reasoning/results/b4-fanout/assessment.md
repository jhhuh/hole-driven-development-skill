# B4 FanOut - HDD Iterative Reasoning Assessment

## 1. Number of Holes

**4 holes** were identified in the skeleton:

| Hole   | Description                                  | Type              |
|--------|----------------------------------------------|-------------------|
| HOLE_1 | Create output channel                        | Data structure    |
| HOLE_2 | Set up WaitGroup for n workers               | Synchronization   |
| HOLE_3 | Spawn n worker goroutines                    | Concurrency logic |
| HOLE_4 | Launch closer goroutine, wait and close out  | Lifecycle mgmt    |

## 2. Fill Order with Reasoning

**Order: HOLE_1 -> HOLE_2 -> HOLE_3 -> HOLE_4**

The fill order follows a strict dependency chain (most constrained first):

1. **HOLE_1 (output channel)** -- Most constrained. Every other hole references `out`. Without it, nothing else can be expressed. No dependencies of its own.

2. **HOLE_2 (WaitGroup setup)** -- Second most constrained. `wg.Add(n)` must be called before any goroutine calls `wg.Done()` (HOLE_3) or `wg.Wait()` (HOLE_4). Calling Add after goroutine launch is a data race.

3. **HOLE_3 (spawn workers)** -- Depends on both HOLE_1 (`out` channel to send to) and HOLE_2 (`wg.Done()` in defer). This is the core computation: read from `input`, apply `fn`, send to `out`.

4. **HOLE_4 (closer goroutine)** -- Least constrained / most dependent. Depends on HOLE_1 (`close(out)`), HOLE_2 (`wg.Wait()`), and logically requires HOLE_3 workers to exist. Must be a goroutine so `FanOut` can return `out` without blocking.

## 3. How Concurrency Concerns Were Decomposed

Each hole isolates a distinct concurrency concern:

- **Channel creation (HOLE_1)**: The communication primitive. Unbuffered channel forces synchronization between producers (workers) and consumer (caller). This is a deliberate choice -- backpressure is applied naturally.

- **Synchronization primitive (HOLE_2)**: WaitGroup tracks goroutine lifetimes. The critical invariant is `Add(n)` before any `Done()`. Placing this as a separate hole made that ordering constraint explicit.

- **Worker fan-out (HOLE_3)**: Multiple goroutines reading from the same channel. Go's channel semantics guarantee each item is received by exactly one goroutine -- no mutex needed. Each worker is independent: `range input` terminates when `input` is closed upstream. `defer wg.Done()` ensures the count decrements even if `fn` panics.

- **Lifecycle management (HOLE_4)**: The closer goroutine bridges the gap between "workers are done" and "output channel is closed." It must be a goroutine because `wg.Wait()` blocks, and the caller needs `out` returned immediately. Without this, either the channel never closes (consumer hangs) or FanOut blocks forever.

**Key concurrency properties achieved:**
- No data races: `input` is read-only, `out` writes are serialized by channel semantics, `wg` follows Add-before-Done ordering.
- No goroutine leaks: all workers terminate when `input` closes; closer terminates after `wg.Wait()`.
- Clean shutdown: `close(out)` signals downstream that all results have been sent.

## 4. Total Tool Calls

| Tool       | Count | Purpose                                    |
|------------|-------|--------------------------------------------|
| Bash       | 4     | ls (2x), go vet, rm go.mod                 |
| Glob       | 3     | Directory exploration, go.mod search, flake |
| Write      | 2     | Initial skeleton, this assessment           |
| Read       | 5     | Verify file state before each edit          |
| Edit       | 4     | Fill HOLE_1, HOLE_2, HOLE_3, HOLE_4        |

**Total: 18 tool calls**
