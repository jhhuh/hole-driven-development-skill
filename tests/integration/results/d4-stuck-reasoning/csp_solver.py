from collections import deque
from typing import Any, Callable
import inspect


def solve_csp(
    variables: list[str],
    domains: dict[str, list[Any]],
    constraints: list[Callable[..., bool]],
) -> dict[str, Any] | None:
    """Generic CSP solver using backtracking with arc consistency."""
    # Deep copy domains so we don't mutate the caller's data
    current_domains = {v: list(d) for v, d in domains.items()}

    # Extract variable scopes from each constraint via parameter inspection
    constraint_scopes = _get_constraint_scopes(constraints)

    # Apply node consistency (unary constraints) then AC-3 (binary constraints)
    if not _ac3(current_domains, constraints, constraint_scopes):
        return None

    # Backtracking search with MAC (maintaining arc consistency)
    return _backtrack(variables, current_domains, constraints, constraint_scopes, {})


def _get_constraint_scopes(
    constraints: list[Callable[..., bool]],
) -> list[list[str]]:
    """Return the list of variable names each constraint depends on."""
    scopes = []
    for c in constraints:
        params = list(inspect.signature(c).parameters.keys())
        scopes.append(params)
    return scopes


def _ac3(
    domains: dict[str, list[Any]],
    constraints: list[Callable[..., bool]],
    constraint_scopes: list[list[str]],
    arcs_for: set[str] | None = None,
) -> bool:
    """Enforce arc consistency. Returns False if any domain is wiped out.

    If arcs_for is given, only re-check arcs involving those variables
    (used for incremental propagation during backtracking).
    """
    # Step 1: Node consistency — apply unary constraints directly
    for c, scope in zip(constraints, constraint_scopes):
        if len(scope) == 1:
            var = scope[0]
            domains[var] = [v for v in domains[var] if c(v)]
            if not domains[var]:
                return False

    # Step 2: Collect binary constraint arcs
    # Each binary constraint (Xi, Xj) produces two arcs: (Xi, Xj, c) and (Xj, Xi, c)
    binary = []
    for c, scope in zip(constraints, constraint_scopes):
        if len(scope) == 2:
            binary.append((scope[0], scope[1], c, scope))

    if not binary:
        return True

    # Build initial queue of arcs
    queue: deque[tuple[str, str, Callable, list[str]]] = deque()
    for xi, xj, c, scope in binary:
        if arcs_for is None or xi in arcs_for or xj in arcs_for:
            queue.append((xi, xj, c, scope))
            queue.append((xj, xi, c, scope))

    # Process arcs until queue is empty
    while queue:
        xi, xj, c, scope = queue.popleft()
        revised = False
        # Determine argument order: scope tells us which param is first/second
        xi_is_first = scope[0] == xi
        new_domain = []
        for vi in domains[xi]:
            # Check if any value in domain(xj) satisfies constraint with vi
            satisfied = False
            for vj in domains[xj]:
                args = (vi, vj) if xi_is_first else (vj, vi)
                if c(*args):
                    satisfied = True
                    break
            if satisfied:
                new_domain.append(vi)
            else:
                revised = True
        if revised:
            domains[xi] = new_domain
            if not domains[xi]:
                return False
            # Re-enqueue all arcs (xk, xi) for other binary constraints
            for c2, scope2 in zip(constraints, constraint_scopes):
                if len(scope2) == 2 and xi in scope2:
                    xk = scope2[0] if scope2[1] == xi else scope2[1]
                    if xk != xj:
                        queue.append((xk, xi, c2, scope2))

    return True


def _is_consistent(
    var: str,
    value: Any,
    assignment: dict[str, Any],
    constraints: list[Callable[..., bool]],
    constraint_scopes: list[list[str]],
) -> bool:
    """Check if assigning var=value is consistent with current assignment."""
    test_assignment = {**assignment, var: value}
    for c, scope in zip(constraints, constraint_scopes):
        # Only check if all variables in scope are assigned in test_assignment
        if all(v in test_assignment for v in scope):
            args = [test_assignment[v] for v in scope]
            if not c(*args):
                return False
    return True


def _select_unassigned(
    variables: list[str],
    domains: dict[str, list[Any]],
    assignment: dict[str, Any],
) -> str:
    """MRV heuristic: pick unassigned variable with smallest domain."""
    unassigned = [v for v in variables if v not in assignment]
    return min(unassigned, key=lambda v: len(domains[v]))


def _backtrack(
    variables: list[str],
    domains: dict[str, list[Any]],
    constraints: list[Callable[..., bool]],
    constraint_scopes: list[list[str]],
    assignment: dict[str, Any],
) -> dict[str, Any] | None:
    """Backtracking search with MAC (maintaining arc consistency)."""
    if len(assignment) == len(variables):
        return dict(assignment)

    var = _select_unassigned(variables, domains, assignment)

    for value in domains[var]:
        if _is_consistent(var, value, assignment, constraints, constraint_scopes):
            assignment[var] = value
            # Save domains and propagate via AC-3
            saved_domains = {v: list(d) for v, d in domains.items()}
            domains[var] = [value]
            if _ac3(domains, constraints, constraint_scopes, arcs_for={var}):
                result = _backtrack(
                    variables, domains, constraints, constraint_scopes, assignment
                )
                if result is not None:
                    return result
            # Restore domains on backtrack
            for v in domains:
                domains[v] = saved_domains[v]
            del assignment[var]

    return None
