"""
Incremental build system with dependency graph, parallel execution, and caching.

Features:
  1. Dependency graph: tasks declare what they depend on
  2. Cycle detection: raise error if circular dependencies exist
  3. Topological ordering: execute tasks in valid dependency order
  4. Parallel execution: independent tasks run concurrently (thread pool)
  5. Incremental builds: hash inputs, skip tasks whose inputs haven't changed
  6. Cache invalidation: if a task's output changes, invalidate all downstream
  7. Dry-run mode: show what would be built without executing
  8. Error handling: if a task fails, cancel pending tasks but let running ones finish

Usage:
  bs = BuildSystem(cache_dir=".build_cache", workers=4)

  @bs.task(deps=["compile"])
  def link(ctx: BuildContext) -> str: ...

  @bs.task(deps=["parse"])
  def compile(ctx: BuildContext) -> str: ...

  @bs.task(deps=[])
  def parse(ctx: BuildContext) -> str: ...

  results = bs.build(["link"])  # builds parse -> compile -> link
  results = bs.build(["link"])  # second run: skips everything (cached)
"""

from dataclasses import dataclass
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor, Future
import hashlib, json, os, threading


@dataclass
class BuildContext:
    task_name: str
    inputs: dict[str, Any]
    cache_dir: str


@dataclass
class _TaskDef:
    name: str
    func: Callable[[BuildContext], Any]
    deps: list[str]


class CycleError(Exception):
    pass


class BuildError(Exception):
    pass


class BuildSystem:
    def __init__(self, cache_dir: str = ".build_cache", workers: int = 4):
        self._tasks: dict[str, _TaskDef] = {}
        self._cache_dir = cache_dir
        self._workers = workers

    def task(self, deps: list[str] | None = None):
        """Decorator to register a task with its dependencies."""
        deps = deps or []

        def decorator(func: Callable[[BuildContext], Any]) -> Callable:
            self._tasks[func.__name__] = _TaskDef(
                name=func.__name__, func=func, deps=list(deps)
            )
            return func

        return decorator

    def build(self, targets: list[str], dry_run: bool = False) -> dict[str, Any]:
        """Build the given targets, returning {task_name: result}."""
        required = self._resolve_deps(targets)
        self._detect_cycle(required)
        order = self._topo_sort(required)
        cache = self._load_cache()
        return self._execute_parallel(order, cache, dry_run)

    # -- internal helpers (holes to be filled) --

    def _resolve_deps(self, targets: list[str]) -> set[str]:
        """Collect all tasks transitively required by targets."""
        required: set[str] = set()
        stack = list(targets)
        while stack:
            name = stack.pop()
            if name in required:
                continue
            if name not in self._tasks:
                raise BuildError(f"Unknown task: {name!r}")
            required.add(name)
            stack.extend(self._tasks[name].deps)
        return required

    def _detect_cycle(self, required: set[str]) -> None:
        """Raise CycleError if the subgraph has a cycle. DFS with 3-color marking."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {n: WHITE for n in required}

        def visit(name: str, path: list[str]) -> None:
            color[name] = GRAY
            for dep in self._tasks[name].deps:
                if dep not in required:
                    continue
                if color[dep] == GRAY:
                    cycle = path[path.index(dep) :] + [dep]
                    raise CycleError(f"Cycle detected: {' -> '.join(cycle)}")
                if color[dep] == WHITE:
                    visit(dep, path + [dep])
            color[name] = BLACK

        for name in required:
            if color[name] == WHITE:
                visit(name, [name])

    def _topo_sort(self, required: set[str]) -> list[str]:
        """Return tasks in a valid execution order (dependencies first). Kahn's algorithm."""
        in_degree: dict[str, int] = {n: 0 for n in required}
        dependents: dict[str, list[str]] = {n: [] for n in required}
        for name in required:
            for dep in self._tasks[name].deps:
                if dep in required:
                    in_degree[name] += 1
                    dependents[dep].append(name)

        queue = sorted(n for n in required if in_degree[n] == 0)
        order: list[str] = []
        while queue:
            name = queue.pop(0)
            order.append(name)
            for dependent in sorted(dependents[name]):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        return order

    def _load_cache(self) -> dict[str, dict]:
        """Load {task_name: {"hash": str, "result": Any}} from disk."""
        path = os.path.join(self._cache_dir, "cache.json")
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def _save_cache(self, cache: dict[str, dict]) -> None:
        """Persist cache to disk."""
        os.makedirs(self._cache_dir, exist_ok=True)
        path = os.path.join(self._cache_dir, "cache.json")
        with open(path, "w") as f:
            json.dump(cache, f, default=str)

    def _hash_inputs(self, task_name: str, dep_results: dict[str, Any]) -> str:
        """Compute a hash of the task's inputs (its dep results)."""
        data = json.dumps(
            {"task": task_name, "deps": dep_results}, sort_keys=True, default=str
        )
        return hashlib.sha256(data.encode()).hexdigest()

    def _execute_parallel(
        self,
        order: list[str],
        cache: dict[str, str],
        dry_run: bool,
    ) -> dict[str, Any]:
        """Execute tasks respecting deps, parallelism, caching, and errors."""
        results: dict[str, Any] = {}
        futures: dict[str, Future] = {}
        lock = threading.Lock()
        cancelled = threading.Event()
        error: list[Exception] = []

        def run_task(name: str) -> tuple[bool, Any]:
            """Returns (was_cached, result)."""
            task_def = self._tasks[name]
            dep_results = {d: results[d] for d in task_def.deps}
            input_hash = self._hash_inputs(name, dep_results)

            cached_entry = cache.get(name)
            if cached_entry and cached_entry.get("hash") == input_hash:
                return (True, cached_entry["result"])

            if cancelled.is_set():
                raise BuildError("Build cancelled due to earlier failure")

            ctx = BuildContext(
                task_name=name, inputs=dep_results, cache_dir=self._cache_dir
            )
            result = task_def.func(ctx)
            cache[name] = {"hash": input_hash, "result": result}
            return (False, result)

        if dry_run:
            would_run: list[str] = []
            for name in order:
                task_def = self._tasks[name]
                dep_results = {d: results.get(d) for d in task_def.deps}
                input_hash = self._hash_inputs(name, dep_results)
                cached_entry = cache.get(name)
                if not cached_entry or cached_entry.get("hash") != input_hash:
                    would_run.append(name)
                results[name] = None
            return {"_dry_run": would_run}

        with ThreadPoolExecutor(max_workers=self._workers) as pool:
            # Track which tasks are ready to submit once deps complete
            pending = set(order)
            submitted: set[str] = set()
            done: set[str] = set()

            def submit_ready() -> None:
                """Submit all tasks whose deps are satisfied."""
                for name in list(pending):
                    if name in submitted:
                        continue
                    task_def = self._tasks[name]
                    if all(d in done for d in task_def.deps):
                        submitted.add(name)
                        futures[name] = pool.submit(run_task, name)

            submit_ready()

            while pending:
                # Wait for any future to complete
                completed_any = False
                for name in list(submitted):
                    if name in done:
                        continue
                    fut = futures.get(name)
                    if fut is None or not fut.done():
                        continue
                    completed_any = True
                    try:
                        _was_cached, result = fut.result()
                        with lock:
                            results[name] = result
                            done.add(name)
                            pending.discard(name)
                    except Exception as e:
                        cancelled.set()
                        error.append(e)
                        with lock:
                            done.add(name)
                            pending.discard(name)
                        # Cancel all pending futures not yet started
                        for pname in list(pending):
                            if pname in futures:
                                futures[pname].cancel()
                            pending.discard(pname)
                        break

                if error:
                    break

                if not completed_any:
                    # Brief sleep to avoid busy-wait, then re-check
                    import time
                    time.sleep(0.001)

                submit_ready()

        if error:
            raise BuildError(f"Task failed: {error[0]}") from error[0]

        self._save_cache(cache)
        return results
