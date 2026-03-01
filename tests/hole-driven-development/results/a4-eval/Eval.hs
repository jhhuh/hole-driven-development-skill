module Eval where

data Expr
  = Lit Int
  | Add Expr Expr
  | Mul Expr Expr
  | Neg Expr

eval :: Expr -> Int
eval (Lit n)   = n
eval (Add l r) = eval l + eval r
eval (Mul l r) = eval l * eval r
eval (Neg e)   = negate (eval e)
