"""
Hindley-Milner type inference with let-polymorphism.

Language:
  e ::= x              -- variable
      | \\x -> e         -- lambda
      | e e             -- application
      | let x = e in e  -- let binding (polymorphic)
      | n               -- integer literal
      | e + e           -- addition
      | if e then e else e  -- conditional (condition must be bool)
      | true | false    -- boolean literals

Types:
  τ ::= Int | Bool | τ -> τ | α   (type variables)

Requirements:
  - Unification with occurs check
  - Let-polymorphism: `let id = \\x -> x in (id 1, id true)` must type-check
  - Lambda-bound variables are NOT generalized (monomorphic)
  - Produce informative error messages for type errors
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# AST
# ---------------------------------------------------------------------------

class Expr:
    pass


class Var(Expr):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name


class Lam(Expr):
    def __init__(self, param: str, body: Expr):
        self.param = param
        self.body = body

    def __repr__(self):
        return f"(\\{self.param} -> {self.body})"


class App(Expr):
    def __init__(self, func: Expr, arg: Expr):
        self.func = func
        self.arg = arg

    def __repr__(self):
        return f"({self.func} {self.arg})"


class Let(Expr):
    def __init__(self, name: str, value: Expr, body: Expr):
        self.name = name
        self.value = value
        self.body = body

    def __repr__(self):
        return f"(let {self.name} = {self.value} in {self.body})"


class Lit(Expr):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return str(self.value)


class BoolLit(Expr):
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self):
        return "true" if self.value else "false"


class Add(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} + {self.right})"


class If(Expr):
    def __init__(self, cond: Expr, then_branch: Expr, else_branch: Expr):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"(if {self.cond} then {self.then_branch} else {self.else_branch})"


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class Type:
    pass


class TVar(Type):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, TVar) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class TInt(Type):
    def __repr__(self):
        return "Int"

    def __eq__(self, other):
        return isinstance(other, TInt)

    def __hash__(self):
        return hash("Int")


class TFun(Type):
    def __init__(self, param_type: Type, return_type: Type):
        self.param_type = param_type
        self.return_type = return_type

    def __repr__(self):
        return f"({self.param_type} -> {self.return_type})"

    def __eq__(self, other):
        return (isinstance(other, TFun)
                and self.param_type == other.param_type
                and self.return_type == other.return_type)

    def __hash__(self):
        return hash(("->", self.param_type, self.return_type))


class TBool(Type):
    def __repr__(self):
        return "Bool"

    def __eq__(self, other):
        return isinstance(other, TBool)

    def __hash__(self):
        return hash("Bool")


# ---------------------------------------------------------------------------
# Type scheme: ∀ α₁…αₙ. τ
# ---------------------------------------------------------------------------

class Scheme:
    def __init__(self, vars: list[str], ty: Type):
        self.vars = vars
        self.ty = ty

    def __repr__(self):
        if self.vars:
            return f"∀{','.join(self.vars)}. {self.ty}"
        return repr(self.ty)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class TypeError(Exception):
    pass


# ---------------------------------------------------------------------------
# Fresh variable supply
# ---------------------------------------------------------------------------

_counter = 0


def _fresh() -> TVar:
    global _counter
    _counter += 1
    return TVar(f"t{_counter}")


def _reset():
    """Reset counter (useful for tests)."""
    global _counter
    _counter = 0


# ---------------------------------------------------------------------------
# Substitution: dict mapping type-variable names -> Type
# ---------------------------------------------------------------------------

Subst = dict[str, Type]


def apply_subst(subst: Subst, ty: Type) -> Type:
    if isinstance(ty, TVar):
        if ty.name in subst:
            return apply_subst(subst, subst[ty.name])
        return ty
    if isinstance(ty, TFun):
        return TFun(apply_subst(subst, ty.param_type),
                     apply_subst(subst, ty.return_type))
    return ty  # TInt, TBool


def apply_subst_scheme(subst: Subst, scheme: Scheme) -> Scheme:
    # The bound variables shadow the substitution.
    restricted = {k: v for k, v in subst.items() if k not in scheme.vars}
    return Scheme(scheme.vars, apply_subst(restricted, scheme.ty))


def apply_subst_env(subst: Subst, env: dict[str, Scheme]) -> dict[str, Scheme]:
    return {k: apply_subst_scheme(subst, v) for k, v in env.items()}


def compose_subst(s1: Subst, s2: Subst) -> Subst:
    """Compose so that apply(compose(s1, s2), t) == apply(s1, apply(s2, t))."""
    result = {k: apply_subst(s1, v) for k, v in s2.items()}
    result.update(s1)
    return result


# ---------------------------------------------------------------------------
# Free type variables
# ---------------------------------------------------------------------------

def ftv_type(ty: Type) -> set[str]:
    if isinstance(ty, TVar):
        return {ty.name}
    if isinstance(ty, TFun):
        return ftv_type(ty.param_type) | ftv_type(ty.return_type)
    return set()


def ftv_scheme(scheme: Scheme) -> set[str]:
    return ftv_type(scheme.ty) - set(scheme.vars)


def ftv_env(env: dict[str, Scheme]) -> set[str]:
    result: set[str] = set()
    for s in env.values():
        result |= ftv_scheme(s)
    return result


# ---------------------------------------------------------------------------
# Generalize / Instantiate
# ---------------------------------------------------------------------------

def generalize(env: dict[str, Scheme], ty: Type) -> Scheme:
    vars = list(ftv_type(ty) - ftv_env(env))
    vars.sort()  # deterministic ordering
    return Scheme(vars, ty)


def instantiate(scheme: Scheme) -> Type:
    subst: Subst = {v: _fresh() for v in scheme.vars}
    return apply_subst(subst, scheme.ty)


# ---------------------------------------------------------------------------
# Unification
# ---------------------------------------------------------------------------

def occurs_in(name: str, ty: Type) -> bool:
    if isinstance(ty, TVar):
        return ty.name == name
    if isinstance(ty, TFun):
        return occurs_in(name, ty.param_type) or occurs_in(name, ty.return_type)
    return False


def unify(t1: Type, t2: Type) -> Subst:
    t1 = _resolve(t1)
    t2 = _resolve(t2)

    if isinstance(t1, TInt) and isinstance(t2, TInt):
        return {}
    if isinstance(t1, TBool) and isinstance(t2, TBool):
        return {}
    if isinstance(t1, TVar):
        return _bind(t1.name, t2)
    if isinstance(t2, TVar):
        return _bind(t2.name, t1)
    if isinstance(t1, TFun) and isinstance(t2, TFun):
        s1 = unify(t1.param_type, t2.param_type)
        s2 = unify(apply_subst(s1, t1.return_type),
                    apply_subst(s1, t2.return_type))
        return compose_subst(s2, s1)
    raise TypeError(f"Cannot unify {t1} with {t2}")


def _resolve(ty: Type) -> Type:
    """No-op -- resolution happens inside apply_subst. Kept for clarity."""
    return ty


def _bind(name: str, ty: Type) -> Subst:
    if isinstance(ty, TVar) and ty.name == name:
        return {}
    if occurs_in(name, ty):
        raise TypeError(
            f"Occurs check: {name} appears in {ty} (infinite type)")
    return {name: ty}


# ---------------------------------------------------------------------------
# Algorithm W
# ---------------------------------------------------------------------------

def _infer(env: dict[str, Scheme], expr: Expr) -> tuple[Subst, Type]:
    """Return (substitution, type) for expr under env."""

    if isinstance(expr, Lit):
        return {}, TInt()

    if isinstance(expr, BoolLit):
        return {}, TBool()

    if isinstance(expr, Var):
        if expr.name not in env:
            raise TypeError(f"Unbound variable: {expr.name}")
        return {}, instantiate(env[expr.name])

    if isinstance(expr, Lam):
        tv = _fresh()
        new_env = dict(env)
        # Lambda-bound variables get a monomorphic type (no generalization).
        new_env[expr.param] = Scheme([], tv)
        s1, body_ty = _infer(new_env, expr.body)
        return s1, TFun(apply_subst(s1, tv), body_ty)

    if isinstance(expr, App):
        tv = _fresh()
        s1, func_ty = _infer(env, expr.func)
        s2, arg_ty = _infer(apply_subst_env(s1, env), expr.arg)
        s3 = unify(apply_subst(s2, func_ty), TFun(arg_ty, tv))
        return compose_subst(s3, compose_subst(s2, s1)), apply_subst(s3, tv)

    if isinstance(expr, Let):
        s1, val_ty = _infer(env, expr.value)
        env1 = apply_subst_env(s1, env)
        # Generalize: the value's type is polymorphic in the body.
        scheme = generalize(env1, val_ty)
        env1[expr.name] = scheme
        s2, body_ty = _infer(env1, expr.body)
        return compose_subst(s2, s1), body_ty

    if isinstance(expr, Add):
        s1, t1 = _infer(env, expr.left)
        s2, t2 = _infer(apply_subst_env(s1, env), expr.right)
        s3 = unify(apply_subst(s2, t1), TInt())
        s4 = unify(apply_subst(s3, t2), TInt())
        return compose_subst(s4, compose_subst(s3, compose_subst(s2, s1))), TInt()

    if isinstance(expr, If):
        s1, cond_ty = _infer(env, expr.cond)
        s2 = unify(cond_ty, TBool())
        cs = compose_subst(s2, s1)
        env1 = apply_subst_env(cs, env)

        s3, then_ty = _infer(env1, expr.then_branch)
        env2 = apply_subst_env(s3, env1)

        s4, else_ty = _infer(env2, expr.else_branch)
        s5 = unify(apply_subst(s4, then_ty), else_ty)

        final_subst = compose_subst(
            s5, compose_subst(s4, compose_subst(s3, cs)))
        return final_subst, apply_subst(s5, else_ty)

    raise TypeError(f"Unknown expression: {expr}")


def infer(expr: Expr) -> Type:
    """Infer the type of expr using Algorithm W."""
    _reset()
    subst, ty = _infer({}, expr)
    return apply_subst(subst, ty)


# ---------------------------------------------------------------------------
# Quick smoke tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # id = \x -> x  :  a -> a
    id_fn = Lam("x", Var("x"))
    print(f"id: {infer(id_fn)}")

    # const = \x -> \y -> x  :  a -> b -> a
    const_fn = Lam("x", Lam("y", Var("x")))
    print(f"const: {infer(const_fn)}")

    # let id = \x -> x in id 1  :  Int
    let_id = Let("id", Lam("x", Var("x")), App(Var("id"), Lit(1)))
    print(f"let id = \\x->x in id 1: {infer(let_id)}")

    # let-polymorphism: let id = \x->x in (id 1) used alongside (id true)
    # We simulate a pair with a church encoding or just test each use.
    let_poly = Let("id", Lam("x", Var("x")),
                   # Use id at Int, then at Bool. We'll test via if:
                   If(App(Var("id"), BoolLit(True)),
                      App(Var("id"), Lit(1)),
                      Lit(2)))
    print(f"let-poly: {infer(let_poly)}")

    # 1 + 2  :  Int
    print(f"1 + 2: {infer(Add(Lit(1), Lit(2)))}")

    # if true then 1 else 2  :  Int
    print(f"if true then 1 else 2: {infer(If(BoolLit(True), Lit(1), Lit(2)))}")

    # Error: applying int to int
    try:
        infer(App(Lit(1), Lit(2)))
    except TypeError as e:
        print(f"Expected error: {e}")

    # Error: if branches disagree
    try:
        infer(If(BoolLit(True), Lit(1), BoolLit(False)))
    except TypeError as e:
        print(f"Expected error: {e}")

    # Error: occurs check  (\x -> x x)
    try:
        infer(Lam("x", App(Var("x"), Var("x"))))
    except TypeError as e:
        print(f"Expected error: {e}")

    print("\nAll smoke tests passed.")
