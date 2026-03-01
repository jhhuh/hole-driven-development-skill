from dataclasses import dataclass
from typing import Union

@dataclass
class Lit:
    value: int

@dataclass
class Add:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Mul:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Neg:
    expr: 'Expr'

Expr = Union[Lit, Add, Mul, Neg]

def eval_expr(expr: Expr) -> int:
    if isinstance(expr, Lit):
        return expr.value
    elif isinstance(expr, Add):
        return eval_expr(expr.left) + eval_expr(expr.right)
    elif isinstance(expr, Mul):
        return eval_expr(expr.left) * eval_expr(expr.right)
    elif isinstance(expr, Neg):
        return -eval_expr(expr.expr)
    else:
        raise TypeError(f"Unknown expression type: {type(expr)}")
