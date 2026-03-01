"""
Hindley-Milner type inference with let-polymorphism.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Union


# ── AST ──────────────────────────────────────────────────────────────

@dataclass
class Var:
    name: str

@dataclass
class Lam:
    param: str
    body: Expr

@dataclass
class App:
    func: Expr
    arg: Expr

@dataclass
class Let:
    name: str
    defn: Expr
    body: Expr

@dataclass
class IntLit:
    value: int

@dataclass
class BoolLit:
    value: bool

@dataclass
class Add:
    left: Expr
    right: Expr

@dataclass
class If:
    cond: Expr
    then_: Expr
    else_: Expr

Expr = Union[Var, Lam, App, Let, IntLit, BoolLit, Add, If]


# ── Types ────────────────────────────────────────────────────────────

class InferenceError(Exception):
    pass

class TVar:
    """Type variable with mutable binding (union-find cell)."""
    _counter = 0
    def __init__(self):
        TVar._counter += 1
        self.id = TVar._counter
        self.bound: Type | None = None
    def __repr__(self):
        return f"t{self.id}"

@dataclass
class TCon:
    """Type constant (Int, Bool)."""
    name: str
    def __repr__(self):
        return self.name

@dataclass
class TFun:
    """Function type: arg -> ret."""
    arg: Type
    ret: Type
    def __repr__(self):
        return f"({self.arg} -> {self.ret})"

Type = Union[TVar, TCon, TFun]

TInt = TCon("Int")
TBool = TCon("Bool")

def prune(t: Type) -> Type:
    """Follow TVar binding chain to its end."""
    if isinstance(t, TVar) and t.bound is not None:
        t.bound = prune(t.bound)
        return t.bound
    return t


# ── Unification ──────────────────────────────────────────────────────

def occurs_in(v: TVar, t: Type) -> bool:
    """Check if type variable v occurs anywhere in type t."""
    t = prune(t)
    if isinstance(t, TVar):
        return v is t
    if isinstance(t, TCon):
        return False
    if isinstance(t, TFun):
        return occurs_in(v, t.arg) or occurs_in(v, t.ret)
    return False

def type_to_str(t: Type) -> str:
    """Pretty-print a type for error messages."""
    t = prune(t)
    if isinstance(t, TVar):
        return repr(t)
    if isinstance(t, TCon):
        return t.name
    if isinstance(t, TFun):
        arg_s = type_to_str(t.arg)
        ret_s = type_to_str(t.ret)
        return f"({arg_s} -> {ret_s})"
    return "?"

def unify(t1: Type, t2: Type) -> None:
    """Unify two types, mutating TVar bindings. Raises InferenceError on failure."""
    t1 = prune(t1)
    t2 = prune(t2)
    if isinstance(t1, TVar):
        if t1 is t2:
            return
        if occurs_in(t1, t2):
            raise InferenceError(f"Infinite type: {type_to_str(t1)} occurs in {type_to_str(t2)}")
        t1.bound = t2
    elif isinstance(t2, TVar):
        unify(t2, t1)
    elif isinstance(t1, TCon) and isinstance(t2, TCon):
        if t1.name != t2.name:
            raise InferenceError(f"Type mismatch: {t1.name} vs {t2.name}")
    elif isinstance(t1, TFun) and isinstance(t2, TFun):
        unify(t1.arg, t2.arg)
        unify(t1.ret, t2.ret)
    else:
        raise InferenceError(f"Cannot unify {type_to_str(t1)} with {type_to_str(t2)}")


# ── Type Environment & Fresh Variables ───────────────────────────────

def fresh_tvar() -> TVar:
    return TVar()

def free_tvars(t: Type) -> set[int]:
    """Collect IDs of all free (unbound) type variables in a type."""
    t = prune(t)
    if isinstance(t, TVar):
        return {t.id}
    if isinstance(t, TCon):
        return set()
    if isinstance(t, TFun):
        return free_tvars(t.arg) | free_tvars(t.ret)
    return set()

def free_tvars_with_refs(t: Type) -> dict[int, TVar]:
    """Like free_tvars but returns id -> TVar mapping."""
    t = prune(t)
    if isinstance(t, TVar):
        return {t.id: t}
    if isinstance(t, TCon):
        return {}
    if isinstance(t, TFun):
        d = free_tvars_with_refs(t.arg)
        d.update(free_tvars_with_refs(t.ret))
        return d
    return {}

@dataclass
class Scheme:
    """Polymorphic type scheme: forall vars. type"""
    vars: list[int]   # quantified TVar IDs
    type: Type

# Environment is a dict from name -> Scheme
Env = dict[str, Scheme]

def free_tvars_scheme(s: Scheme) -> set[int]:
    return free_tvars(s.type) - set(s.vars)

def free_tvars_env(env: Env) -> set[int]:
    result: set[int] = set()
    for s in env.values():
        result |= free_tvars_scheme(s)
    return result

def generalize(env: Env, t: Type) -> Scheme:
    """Generalize a type over all free vars not free in env."""
    env_free = free_tvars_env(env)
    t_free = free_tvars(t)
    quantified = sorted(t_free - env_free)
    return Scheme(quantified, t)

def instantiate(scheme: Scheme) -> Type:
    """Replace quantified variables with fresh type variables."""
    if not scheme.vars:
        return scheme.type
    # Build mapping from old TVar id -> new fresh TVar
    subst: dict[int, TVar] = {v: fresh_tvar() for v in scheme.vars}
    def apply(t: Type) -> Type:
        t = prune(t)
        if isinstance(t, TVar):
            return subst.get(t.id, t)
        if isinstance(t, TCon):
            return t
        if isinstance(t, TFun):
            return TFun(apply(t.arg), apply(t.ret))
        return t
    return apply(scheme.type)


# ── Inference ────────────────────────────────────────────────────────

def infer(env: Env, expr: Expr) -> Type:
    """Infer the type of expr in the given environment."""
    if isinstance(expr, IntLit):
        return TInt

    if isinstance(expr, BoolLit):
        return TBool

    if isinstance(expr, Var):
        if expr.name not in env:
            raise InferenceError(f"Unbound variable: {expr.name}")
        return instantiate(env[expr.name])

    if isinstance(expr, Lam):
        param_ty = fresh_tvar()
        # Lambda-bound variables are monomorphic: Scheme with no quantified vars
        new_env = {**env, expr.param: Scheme([], param_ty)}
        body_ty = infer(new_env, expr.body)
        return TFun(param_ty, body_ty)

    if isinstance(expr, App):
        func_ty = infer(env, expr.func)
        arg_ty = infer(env, expr.arg)
        result_ty = fresh_tvar()
        unify(func_ty, TFun(arg_ty, result_ty))
        return result_ty

    if isinstance(expr, Let):
        defn_ty = infer(env, expr.defn)
        scheme = generalize(env, defn_ty)
        new_env = {**env, expr.name: scheme}
        return infer(new_env, expr.body)

    if isinstance(expr, Add):
        left_ty = infer(env, expr.left)
        right_ty = infer(env, expr.right)
        unify(left_ty, TInt)
        unify(right_ty, TInt)
        return TInt

    if isinstance(expr, If):
        cond_ty = infer(env, expr.cond)
        unify(cond_ty, TBool)
        then_ty = infer(env, expr.then_)
        else_ty = infer(env, expr.else_)
        unify(then_ty, else_ty)
        return then_ty

    raise InferenceError(f"Unknown expression type: {type(expr)}")


# ── Public API & Tests ───────────────────────────────────────────────

def infer_expr(expr: Expr, env: Env | None = None) -> Type:
    """Infer the type of an expression. Returns the pruned result type."""
    if env is None:
        env = {}
    t = infer(env, expr)
    return prune(t)


if __name__ == "__main__":
    passed = 0
    failed = 0

    def test(name: str, expr: Expr, expected: str, should_fail: bool = False):
        global passed, failed
        # Reset TVar counter for reproducible output
        TVar._counter = 0
        try:
            t = infer_expr(expr)
            result = type_to_str(t)
            if should_fail:
                print(f"FAIL {name}: expected error but got {result}")
                failed += 1
            elif result == expected:
                print(f"  OK {name}: {result}")
                passed += 1
            else:
                print(f"FAIL {name}: expected {expected}, got {result}")
                failed += 1
        except InferenceError as e:
            if should_fail:
                print(f"  OK {name}: raised InferenceError: {e}")
                passed += 1
            else:
                print(f"FAIL {name}: unexpected InferenceError: {e}")
                failed += 1

    # Literals
    test("int literal", IntLit(42), "Int")
    test("bool literal", BoolLit(True), "Bool")

    # Lambda: \x -> x  should be  t1 -> t1
    test("identity", Lam("x", Var("x")), "(t1 -> t1)")

    # Application: (\x -> x) 1  should be  Int
    test("apply id to int", App(Lam("x", Var("x")), IntLit(1)), "Int")

    # Addition
    test("add", Add(IntLit(1), IntLit(2)), "Int")

    # If-then-else
    test("if bool", If(BoolLit(True), IntLit(1), IntLit(2)), "Int")

    # Let-polymorphism: let id = \x -> x in (id 1) + ... should work
    # id is used at Int
    test("let mono use",
         Let("id", Lam("x", Var("x")), App(Var("id"), IntLit(5))),
         "Int")

    # Let-polymorphism: id used at two different types
    # let id = \x -> x in if (id true) then (id 1) else 0
    test("let polymorphism",
         Let("id", Lam("x", Var("x")),
             If(App(Var("id"), BoolLit(True)),
                App(Var("id"), IntLit(1)),
                IntLit(0))),
         "Int")

    # Lambda-bound vars are NOT polymorphic:
    # \f -> if (f true) then (f 1) else 0  should FAIL
    test("lambda mono",
         Lam("f", If(App(Var("f"), BoolLit(True)),
                      App(Var("f"), IntLit(1)),
                      IntLit(0))),
         "", should_fail=True)

    # Unbound variable
    test("unbound var", Var("x"), "", should_fail=True)

    # Add bool should fail
    test("add bool", Add(BoolLit(True), IntLit(1)), "", should_fail=True)

    # If with non-bool condition
    test("if non-bool cond", If(IntLit(1), IntLit(2), IntLit(3)), "", should_fail=True)

    # If branch mismatch
    test("if branch mismatch", If(BoolLit(True), IntLit(1), BoolLit(False)), "", should_fail=True)

    # Occurs check: \x -> x x  should fail
    test("occurs check", Lam("x", App(Var("x"), Var("x"))), "", should_fail=True)

    # Nested let-polymorphism
    # let id = \x -> x in let f = id in f 1
    test("nested let poly",
         Let("id", Lam("x", Var("x")),
             Let("f", Var("id"),
                 App(Var("f"), IntLit(1)))),
         "Int")

    # \x -> x + 1  should be  Int -> Int
    test("lambda add",
         Lam("x", Add(Var("x"), IntLit(1))),
         "(Int -> Int)")

    # let const = \x -> \y -> x in const 1 true  should be  Int
    test("const function",
         Let("const", Lam("x", Lam("y", Var("x"))),
             App(App(Var("const"), IntLit(1)), BoolLit(True))),
         "Int")

    print(f"\n{passed} passed, {failed} failed")
    if failed > 0:
        raise SystemExit(1)
