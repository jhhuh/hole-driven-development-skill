module TypeCheck where

data Type = TInt | TBool | TFun Type Type deriving (Eq, Show)
data Term = TmLit Int | TmBool Bool | TmVar String
           | TmApp Term Term | TmAbs String Type Term
           | TmIf Term Term Term

type Env = [(String, Type)]

typeCheck :: Env -> Term -> Either String Type
typeCheck _ (TmLit _) = Right TInt
typeCheck _ (TmBool _) = Right TBool
typeCheck env (TmVar x) =
  case lookup x env of
    Just t  -> Right t
    Nothing -> Left $ "Unbound variable: " ++ x
typeCheck env (TmAbs x ty body) = do
  bodyTy <- typeCheck ((x, ty) : env) body
  Right (TFun ty bodyTy)
typeCheck env (TmApp fn arg) = do
  fnTy  <- typeCheck env fn
  argTy <- typeCheck env arg
  case fnTy of
    TFun paramTy resTy
      | paramTy == argTy -> Right resTy
      | otherwise -> Left $ "Argument type mismatch: expected " ++ show paramTy ++ ", got " ++ show argTy
    _ -> Left $ "Expected function type, got " ++ show fnTy
typeCheck env (TmIf cond thn els) = do
  condTy <- typeCheck env cond
  case condTy of
    TBool -> do
      thnTy <- typeCheck env thn
      elsTy <- typeCheck env els
      if thnTy == elsTy
        then Right thnTy
        else Left $ "Branch type mismatch: " ++ show thnTy ++ " vs " ++ show elsTy
    _ -> Left $ "Condition must be TBool, got " ++ show condTy
