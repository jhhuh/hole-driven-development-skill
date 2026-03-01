module TypeCheck where

data Type = TInt | TBool | TFun Type Type deriving (Eq, Show)

data Term
  = TmLit Int
  | TmBool Bool
  | TmVar String
  | TmApp Term Term
  | TmAbs String Type Term
  | TmIf Term Term Term
  deriving Show

type Env = [(String, Type)]

typeCheck :: Env -> Term -> Either String Type
typeCheck env (TmLit _n)            = Right TInt
typeCheck env (TmBool _b)           = Right TBool
typeCheck env (TmVar x)             = case lookup x env of
  Just ty -> Right ty
  Nothing -> Left ("Unbound variable: " ++ x)
typeCheck env (TmApp t1 t2)         = do
  funTy <- typeCheck env t1
  argTy <- typeCheck env t2
  case funTy of
    TFun paramTy resTy
      | argTy == paramTy -> Right resTy
      | otherwise -> Left ("Argument type mismatch: expected " ++ show paramTy ++ ", got " ++ show argTy)
    _ -> Left ("Expected function type, got " ++ show funTy)
typeCheck env (TmAbs x ty body)     = do
  bodyTy <- typeCheck ((x, ty) : env) body
  Right (TFun ty bodyTy)
typeCheck env (TmIf cond t1 t2)     = do
  condTy <- typeCheck env cond
  ty1 <- typeCheck env t1
  ty2 <- typeCheck env t2
  if condTy /= TBool
    then Left ("Condition must be Bool, got " ++ show condTy)
    else if ty1 /= ty2
      then Left ("Branch type mismatch: " ++ show ty1 ++ " vs " ++ show ty2)
      else Right ty1
