"""
Hindley-Milner type inference with let-polymorphism.

Language:
  e ::= x | \\x -> e | e e | let x = e in e | n | e + e | if e then e else e | true | false

Types:
  τ ::= Int | Bool | τ -> τ | α   (type variables)
"""

from dataclasses import dataclass
from typing import Dict, Set, Tuple


# ── AST ──────────────────────────────────────────────────────────────────

class Expr:
    pass

@dataclass
class Var(Expr):
    name: str

@dataclass
class Lam(Expr):
    param: str
    body: Expr

@dataclass
class App(Expr):
    func: Expr
    arg: Expr

@dataclass
class Let(Expr):
    name: str
    value: Expr
    body: Expr

@dataclass
class Lit(Expr):
    value: int

@dataclass
class BoolLit(Expr):
    value: bool

@dataclass
class Add(Expr):
    left: Expr
    right: Expr

@dataclass
class If(Expr):
    cond: Expr
    then_branch: Expr
    else_branch: Expr


# ── Types ────────────────────────────────────────────────────────────────

class Type:
    pass

@dataclass(frozen=True)
class TVar(Type):
    name: str

@dataclass(frozen=True)
class TInt(Type):
    pass

@dataclass(frozen=True)
class TBool(Type):
    pass

@dataclass(frozen=True)
class TFun(Type):
    param_type: Type
    return_type: Type


# ── Type Inference Error ─────────────────────────────────────────────────

class TypeError(Exception):
    pass


# ── Substitution ─────────────────────────────────────────────────────────

Subst = Dict[str, Type]


def apply_subst(subst: Subst, ty: Type) -> Type:
    """Apply substitution to a type."""
    if isinstance(ty, TVar):
        return subst.get(ty.name, ty)
    elif isinstance(ty, (TInt, TBool)):
        return ty
    elif isinstance(ty, TFun):
        return TFun(apply_subst(subst, ty.param_type), apply_subst(subst, ty.return_type))
    raise TypeError(f"Unknown type: {ty}")


def apply_subst_env(subst: Subst, env: "TypeEnv") -> "TypeEnv":
    """Apply substitution to every scheme in a type environment."""
    return {k: apply_subst_scheme(subst, v) for k, v in env.items()}


def compose_subst(s1: Subst, s2: Subst) -> Subst:
    """Compose two substitutions: (s1 ∘ s2). Apply s1 to the range of s2, then merge."""
    applied = {k: apply_subst(s1, v) for k, v in s2.items()}
    return {**s1, **applied}


# ── Free Type Variables ──────────────────────────────────────────────────

def ftv_type(ty: Type) -> Set[str]:
    """Free type variables of a type."""
    if isinstance(ty, TVar):
        return {ty.name}
    elif isinstance(ty, (TInt, TBool)):
        return set()
    elif isinstance(ty, TFun):
        return ftv_type(ty.param_type) | ftv_type(ty.return_type)
    raise TypeError(f"Unknown type: {ty}")


def ftv_scheme(scheme: "Scheme") -> Set[str]:
    """Free type variables of a type scheme."""
    return ftv_type(scheme.ty) - set(scheme.vars)


def ftv_env(env: "TypeEnv") -> Set[str]:
    """Free type variables of an environment."""
    result: Set[str] = set()
    for scheme in env.values():
        result |= ftv_scheme(scheme)
    return result


# ── Unification ──────────────────────────────────────────────────────────

def occurs_in(var_name: str, ty: Type) -> bool:
    """Occurs check: does var_name appear in ty?"""
    return var_name in ftv_type(ty)


def unify(t1: Type, t2: Type) -> Subst:
    """Unify two types, returning a most-general unifier substitution."""
    if isinstance(t1, TInt) and isinstance(t2, TInt):
        return {}
    if isinstance(t1, TBool) and isinstance(t2, TBool):
        return {}
    if isinstance(t1, TVar):
        if t1 == t2:
            return {}
        if occurs_in(t1.name, t2):
            raise TypeError(f"Infinite type: {t1.name} occurs in {t2}")
        return {t1.name: t2}
    if isinstance(t2, TVar):
        return unify(t2, t1)
    if isinstance(t1, TFun) and isinstance(t2, TFun):
        s1 = unify(t1.param_type, t2.param_type)
        s2 = unify(apply_subst(s1, t1.return_type), apply_subst(s1, t2.return_type))
        return compose_subst(s2, s1)
    raise TypeError(f"Cannot unify {t1} with {t2}")


# ── Type Schemes & Generalization ────────────────────────────────────────

@dataclass
class Scheme:
    """∀ vars. ty"""
    vars: list  # list of bound type variable names
    ty: Type


TypeEnv = Dict[str, Scheme]

_counter = 0

def fresh_tvar() -> TVar:
    """Generate a fresh type variable."""
    global _counter
    _counter += 1
    return TVar(f"t{_counter}")


def generalize(env: TypeEnv, ty: Type) -> Scheme:
    """Generalize a type over variables not free in the environment."""
    vars = list(ftv_type(ty) - ftv_env(env))
    return Scheme(vars, ty)


def instantiate(scheme: Scheme) -> Type:
    """Instantiate a scheme with fresh type variables."""
    subst = {v: fresh_tvar() for v in scheme.vars}
    return apply_subst(subst, scheme.ty)


def apply_subst_scheme(subst: Subst, scheme: Scheme) -> Scheme:
    """Apply substitution to a scheme (avoiding capture of bound vars)."""
    restricted = {k: v for k, v in subst.items() if k not in scheme.vars}
    return Scheme(scheme.vars, apply_subst(restricted, scheme.ty))


# ── Algorithm W ──────────────────────────────────────────────────────────

def w(env: TypeEnv, expr: Expr) -> Tuple[Subst, Type]:
    """Algorithm W: infer type of expr in env, returning (substitution, type)."""

    if isinstance(expr, Lit):
        return {}, TInt()

    if isinstance(expr, BoolLit):
        return {}, TBool()

    if isinstance(expr, Var):
        if expr.name not in env:
            raise TypeError(f"Unbound variable: {expr.name}")
        return {}, instantiate(env[expr.name])

    if isinstance(expr, Lam):
        tv = fresh_tvar()
        new_env = {**env, expr.param: Scheme([], tv)}
        s1, t1 = w(new_env, expr.body)
        return s1, TFun(apply_subst(s1, tv), t1)

    if isinstance(expr, App):
        tv = fresh_tvar()
        s1, t1 = w(env, expr.func)
        s2, t2 = w(apply_subst_env(s1, env), expr.arg)
        s3 = unify(apply_subst(s2, t1), TFun(t2, tv))
        return compose_subst(s3, compose_subst(s2, s1)), apply_subst(s3, tv)

    if isinstance(expr, Let):
        s1, t1 = w(env, expr.value)
        env1 = apply_subst_env(s1, env)
        scheme = generalize(env1, t1)
        s2, t2 = w({**env1, expr.name: scheme}, expr.body)
        return compose_subst(s2, s1), t2

    if isinstance(expr, Add):
        s1, t1 = w(env, expr.left)
        s2, t2 = w(apply_subst_env(s1, env), expr.right)
        s3 = unify(apply_subst(s2, t1), TInt())
        s4 = unify(apply_subst(s3, t2), TInt())
        return compose_subst(s4, compose_subst(s3, compose_subst(s2, s1))), TInt()

    if isinstance(expr, If):
        s1, t1 = w(env, expr.cond)
        s2 = unify(t1, TBool())
        env1 = apply_subst_env(compose_subst(s2, s1), env)
        s3, t2 = w(env1, expr.then_branch)
        env2 = apply_subst_env(s3, env1)
        s4, t3 = w(env2, expr.else_branch)
        s5 = unify(apply_subst(s4, t2), t3)
        combined = compose_subst(s5, compose_subst(s4, compose_subst(s3, compose_subst(s2, s1))))
        return combined, apply_subst(s5, t3)

    raise TypeError(f"Unknown expression: {expr}")


def infer(expr: Expr) -> Type:
    """Infer the type of expr using Algorithm W."""
    global _counter
    _counter = 0
    s, t = w({}, expr)
    return apply_subst(s, t)
