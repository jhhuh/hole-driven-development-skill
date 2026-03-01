"""Incremental build system with dependency graph, parallel execution, and caching."""

from __future__ import annotations

import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set


@dataclass
class BuildContext:
    """Context passed to each task function during execution."""
    task_name: str
    dep_results: Dict[str, str]
    cache_dir: Path


class CycleError(Exception):
    """Raised when a circular dependency is detected."""
    pass


def detect_cycles(deps: Dict[str, List[str]]) -> None:
    """Raise CycleError if the dependency graph contains a cycle. DFS 3-color."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[str, int] = {name: WHITE for name in deps}

    def visit(node: str, path: List[str]) -> None:
        color[node] = GRAY
        path.append(node)
        for dep in deps.get(node, []):
            if dep not in color:
                continue  # unknown dep -- will be caught at build time
            if color[dep] == GRAY:
                cycle_start = path.index(dep)
                cycle = path[cycle_start:] + [dep]
                raise CycleError(f"Circular dependency: {' -> '.join(cycle)}")
            if color[dep] == WHITE:
                visit(dep, path)
        path.pop()
        color[node] = BLACK

    for node in deps:
        if color[node] == WHITE:
            visit(node, [])


def topo_sort(deps: Dict[str, List[str]], targets: List[str]) -> List[str]:
    """Return tasks reachable from targets in dependency-first order."""
    visited: Set[str] = set()
    order: List[str] = []

    def visit(node: str) -> None:
        if node in visited:
            return
        visited.add(node)
        for dep in deps.get(node, []):
            visit(dep)
        order.append(node)

    for target in targets:
        visit(target)
    return order


def compute_input_hash(task_name: str, dep_results: Dict[str, str]) -> str:
    """Deterministic hash of a task's identity + its dependency outputs."""
    h = hashlib.sha256()
    h.update(task_name.encode())
    for dep_name in sorted(dep_results):
        h.update(dep_name.encode())
        h.update(dep_results[dep_name].encode())
    return h.hexdigest()


def _cache_path(cache_dir: Path, task_name: str) -> Path:
    return cache_dir / f"{task_name}.json"


def cache_load(cache_dir: Path, task_name: str, input_hash: str) -> Optional[str]:
    """Load cached result if input_hash matches. Returns None on miss."""
    path = _cache_path(cache_dir, task_name)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if data.get("input_hash") == input_hash:
            return data["result"]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def cache_save(cache_dir: Path, task_name: str, input_hash: str, result: str) -> None:
    """Save task result and input hash to cache."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = _cache_path(cache_dir, task_name)
    path.write_text(json.dumps({"input_hash": input_hash, "result": result}))


class _BuildError(Exception):
    """Wraps a task failure with the task name."""
    def __init__(self, task_name: str, cause: Exception):
        self.task_name = task_name
        self.cause = cause
        super().__init__(f"Task '{task_name}' failed: {cause}")


def execute_parallel(
    ordered: List[str],
    deps: Dict[str, List[str]],
    tasks: Dict[str, Callable],
    cache_dir: Path,
    workers: int,
) -> Dict[str, str]:
    """Execute tasks in dependency order using a thread pool. Returns task->result map."""
    results: Dict[str, str] = {}
    results_lock = threading.Lock()
    cancelled = threading.Event()
    error: Optional[_BuildError] = None
    error_lock = threading.Lock()

    # Track completion for dependency gating
    done_events: Dict[str, threading.Event] = {name: threading.Event() for name in ordered}
    changed_tasks: Set[str] = set()

    def run_task(task_name: str) -> None:
        nonlocal error
        # Wait for all deps to finish
        for dep in deps.get(task_name, []):
            if dep in done_events:
                done_events[dep].wait()
        if cancelled.is_set():
            done_events[task_name].set()
            return

        try:
            with results_lock:
                dep_results = {d: results[d] for d in deps.get(task_name, []) if d in results}

            input_hash = compute_input_hash(task_name, dep_results)
            cached = cache_load(cache_dir, task_name, input_hash)

            if cached is not None:
                with results_lock:
                    results[task_name] = cached
            else:
                ctx = BuildContext(
                    task_name=task_name, dep_results=dep_results, cache_dir=cache_dir
                )
                result = tasks[task_name](ctx)
                cache_save(cache_dir, task_name, input_hash, result)
                with results_lock:
                    results[task_name] = result
                    changed_tasks.add(task_name)
        except Exception as e:
            with error_lock:
                if error is None:
                    error = _BuildError(task_name, e)
            cancelled.set()
        finally:
            done_events[task_name].set()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures: List[Future] = []
        for task_name in ordered:
            if cancelled.is_set():
                done_events[task_name].set()
                continue
            futures.append(pool.submit(run_task, task_name))

        # Wait for all submitted futures (running ones finish even if cancelled)
        for f in futures:
            f.result()

    if error is not None:
        raise error

    # Invalidate downstream of changed tasks (only those not built in this run)
    if changed_tasks:
        built_this_run = set(ordered)
        invalidate_downstream(changed_tasks, deps, cache_dir, already_built=built_this_run)

    return results


def invalidate_downstream(
    changed: Set[str],
    deps: Dict[str, List[str]],
    cache_dir: Path,
    already_built: Optional[Set[str]] = None,
) -> Set[str]:
    """Delete cache for transitive dependents of changed tasks (excluding already_built)."""
    already_built = already_built or set()
    # Build reverse graph: task -> list of tasks that depend on it
    reverse: Dict[str, List[str]] = {}
    for task, task_deps in deps.items():
        for d in task_deps:
            reverse.setdefault(d, []).append(task)

    # BFS from changed tasks through reverse edges
    invalidated: Set[str] = set()
    queue = list(changed)
    while queue:
        node = queue.pop()
        for dependent in reverse.get(node, []):
            if dependent not in invalidated and dependent not in already_built:
                invalidated.add(dependent)
                path = _cache_path(cache_dir, dependent)
                if path.exists():
                    path.unlink()
                queue.append(dependent)
    return invalidated


def dry_run_plan(
    ordered: List[str], deps: Dict[str, List[str]], cache_dir: Path
) -> List[tuple]:
    """Simulate build, reporting what would run. Returns list of (task, action, reason)."""
    results: Dict[str, str] = {}
    plan: List[tuple] = []

    for task_name in ordered:
        dep_results = {d: results[d] for d in deps.get(task_name, []) if d in results}
        input_hash = compute_input_hash(task_name, dep_results)
        cached = cache_load(cache_dir, task_name, input_hash)
        if cached is not None:
            results[task_name] = cached
            plan.append((task_name, "skip", "cached"))
        else:
            results[task_name] = f"<would-build:{task_name}>"
            plan.append((task_name, "build", "inputs changed or not cached"))

    return plan


class BuildSystem:
    """Main build system. Register tasks with @bs.task, run with bs.build()."""

    def __init__(self, cache_dir: str = ".build_cache", workers: int = 4):
        self.cache_dir = Path(cache_dir)
        self.workers = workers
        self._tasks: Dict[str, Callable] = {}
        self._deps: Dict[str, List[str]] = {}

    def task(self, deps: Optional[List[str]] = None):
        """Decorator to register a build task with its dependencies."""
        deps = deps or []

        def decorator(fn: Callable) -> Callable:
            name = fn.__name__
            self._tasks[name] = fn
            self._deps[name] = deps
            return fn

        return decorator

    def build(self, targets: List[str], dry_run: bool = False) -> Dict[str, str]:
        """Build the given targets. Returns dict of task_name -> result."""
        # Validate all targets and their transitive deps are registered
        for target in targets:
            if target not in self._tasks:
                raise ValueError(f"Unknown task: '{target}'")

        # Validate all deps reference known tasks
        for task_name, task_deps in self._deps.items():
            for dep in task_deps:
                if dep not in self._tasks:
                    raise ValueError(
                        f"Task '{task_name}' depends on unknown task '{dep}'"
                    )

        # Cycle detection
        detect_cycles(self._deps)

        # Topological ordering (deps before dependents)
        ordered = topo_sort(self._deps, targets)

        if dry_run:
            plan = dry_run_plan(ordered, self._deps, self.cache_dir)
            # Return plan as dict for dry-run: task -> "skip:reason" or "build:reason"
            return {name: f"{action}: {reason}" for name, action, reason in plan}

        # Execute with parallel engine
        return execute_parallel(
            ordered, self._deps, self._tasks, self.cache_dir, self.workers
        )
