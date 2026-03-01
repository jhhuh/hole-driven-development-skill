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
  def link(ctx: BuildContext) -> str:
      return "linked binary path"

  @bs.task(deps=["parse"])
  def compile(ctx: BuildContext) -> str:
      return "compiled object path"

  @bs.task(deps=[])
  def parse(ctx: BuildContext) -> str:
      return "parsed AST path"

  results = bs.build(["link"])  # builds parse -> compile -> link
  results = bs.build(["link"])  # second run: skips everything (cached)
"""

from dataclasses import dataclass
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor, Future
import hashlib
import inspect
import json
import os
import threading


@dataclass
class BuildContext:
    task_name: str
    inputs: dict[str, Any]  # dependency name -> output
    cache_dir: str


class CycleError(Exception):
    pass


class BuildError(Exception):
    def __init__(self, task_name: str, original: Exception):
        self.task_name = task_name
        self.original = original
        super().__init__(f"Task '{task_name}' failed: {original}")


class BuildSystem:
    def __init__(self, cache_dir: str = ".build_cache", workers: int = 4):
        self._tasks: dict[str, Callable] = {}
        self._deps: dict[str, list[str]] = {}
        self._cache_dir = cache_dir
        self._workers = workers

    def task(self, deps: list[str] | None = None):
        """Decorator to register a build task."""
        deps = deps or []

        def decorator(fn: Callable) -> Callable:
            name = fn.__name__
            self._tasks[name] = fn
            self._deps[name] = list(deps)
            return fn

        return decorator

    def build(self, targets: list[str], dry_run: bool = False) -> dict[str, Any]:
        """Build specified targets and their dependencies."""
        order = self._topo_sort(targets)

        if dry_run:
            return {name: None for name in order}

        os.makedirs(self._cache_dir, exist_ok=True)

        lock = threading.Lock()
        results: dict[str, Any] = {}
        errors: list[BuildError] = []
        done: dict[str, threading.Event] = {name: threading.Event() for name in order}

        def run_task(name: str) -> None:
            # Wait for all dependencies to complete.
            for dep in self._deps[name]:
                done[dep].wait()

            # If an earlier task failed, don't start new work.
            with lock:
                if errors:
                    done[name].set()
                    return
                inputs = {dep: results[dep] for dep in self._deps[name]}

            # Check cache.
            cache_key = self._cache_key(name, inputs)
            cached = self._load_cache(cache_key)
            if cached is not None:
                with lock:
                    results[name] = cached
                done[name].set()
                return

            # Execute the task.
            ctx = BuildContext(task_name=name, inputs=inputs, cache_dir=self._cache_dir)
            try:
                output = self._tasks[name](ctx)
            except Exception as exc:
                with lock:
                    errors.append(BuildError(name, exc))
                done[name].set()
                return

            with lock:
                results[name] = output
            self._save_cache(cache_key, name, output)
            done[name].set()

        with ThreadPoolExecutor(max_workers=self._workers) as pool:
            futures: list[Future] = []
            for name in order:
                futures.append(pool.submit(run_task, name))
            for f in futures:
                f.result()

        if errors:
            raise errors[0]

        return results

    # ------------------------------------------------------------------
    # Topological sort with cycle detection (Kahn's algorithm)
    # ------------------------------------------------------------------

    def _topo_sort(self, targets: list[str]) -> list[str]:
        """Return tasks in dependency-first order. Raises CycleError on cycles."""
        # Collect the subgraph reachable from targets.
        needed: set[str] = set()
        stack = list(targets)
        while stack:
            name = stack.pop()
            if name in needed:
                continue
            if name not in self._tasks:
                raise KeyError(f"Unknown task: '{name}'")
            needed.add(name)
            for dep in self._deps[name]:
                if dep not in needed:
                    stack.append(dep)

        # Kahn's algorithm.
        # Edge dep -> n means "dep must run before n".
        # in_degree[n] = number of dependencies n has within the subgraph.
        in_degree: dict[str, int] = {n: 0 for n in needed}
        for n in needed:
            for dep in self._deps[n]:
                in_degree[n] += 1

        queue = [n for n in needed if in_degree[n] == 0]
        order: list[str] = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            # Find tasks in the subgraph that list `node` as a dependency.
            for n in needed:
                if node in self._deps[n]:
                    in_degree[n] -= 1
                    if in_degree[n] == 0:
                        queue.append(n)

        if len(order) != len(needed):
            remaining = needed - set(order)
            raise CycleError(f"Circular dependency among: {remaining}")

        return order

    # ------------------------------------------------------------------
    # Caching
    # ------------------------------------------------------------------

    def _cache_key(self, task_name: str, inputs: dict[str, Any]) -> str:
        """Deterministic hash of task identity + dependency outputs.

        Because dependency outputs are included, a changed upstream result
        naturally produces a different key for all downstream tasks. This
        gives us automatic cache invalidation through the dependency chain.
        """
        fn = self._tasks[task_name]
        try:
            fn_source = inspect.getsource(fn)
        except (OSError, TypeError):
            fn_source = fn.__qualname__

        blob = json.dumps(
            {"task": task_name, "fn": fn_source, "inputs": inputs},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(blob.encode()).hexdigest()

    def _cache_path(self, key: str) -> str:
        return os.path.join(self._cache_dir, f"{key}.json")

    def _load_cache(self, key: str) -> Any | None:
        path = self._cache_path(key)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                entry = json.load(f)
            return entry["value"]
        except (json.JSONDecodeError, KeyError, OSError):
            return None

    def _save_cache(self, key: str, task_name: str, value: Any) -> None:
        path = self._cache_path(key)
        try:
            with open(path, "w") as f:
                json.dump({"task": task_name, "value": value}, f, default=str)
        except (TypeError, OSError):
            pass

    def invalidate(self, task_name: str) -> None:
        """Remove cached results for a task and all its transitive dependents.

        Normally this isn't needed -- cache keys incorporate dependency outputs,
        so a changed upstream automatically misses downstream caches. But if
        external state changed (files on disk, env vars) while function source
        stayed the same, explicit invalidation forces a rebuild.
        """
        to_clear = self._transitive_dependents(task_name)
        if not os.path.isdir(self._cache_dir):
            return
        for filename in os.listdir(self._cache_dir):
            path = os.path.join(self._cache_dir, filename)
            try:
                with open(path, "r") as f:
                    entry = json.load(f)
                if entry.get("task") in to_clear:
                    os.remove(path)
            except (json.JSONDecodeError, KeyError, OSError):
                pass

    def _transitive_dependents(self, task_name: str) -> set[str]:
        """Return task_name plus every task that transitively depends on it."""
        result: set[str] = set()
        stack = [task_name]
        while stack:
            current = stack.pop()
            if current in result:
                continue
            result.add(current)
            for name, deps in self._deps.items():
                if current in deps and name not in result:
                    stack.append(name)
        return result
