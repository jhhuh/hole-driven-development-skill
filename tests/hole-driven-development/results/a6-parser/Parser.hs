module Parser where

import Data.Char (isDigit, digitToInt)

data Expr = Num Int | BinOp Char Expr Expr
  deriving Show

-- | Parse an arithmetic expression
-- expr   = term (('+' | '-') term)*
-- term   = factor (('*' | '/') factor)*
-- factor = '(' expr ')' | number
parseExpr :: String -> Maybe (Expr, String)
parseExpr s = case parseTerm s of
  Just (left, rest) -> exprLoop left rest
  Nothing           -> Nothing
  where
    exprLoop l (op:rest') | op == '+' || op == '-' =
      case parseTerm rest' of
        Just (r, rest'') -> exprLoop (BinOp op l r) rest''
        Nothing          -> Nothing
    exprLoop l rest' = Just (l, rest')

parseTerm :: String -> Maybe (Expr, String)
parseTerm s = case parseFactor s of
  Just (left, rest) -> termLoop left rest
  Nothing           -> Nothing
  where
    termLoop l (op:rest') | op == '*' || op == '/' =
      case parseFactor rest' of
        Just (r, rest'') -> termLoop (BinOp op l r) rest''
        Nothing          -> Nothing
    termLoop l rest' = Just (l, rest')

parseFactor :: String -> Maybe (Expr, String)
parseFactor ('(':rest) = case parseExpr rest of
  Just (e, ')':rest') -> Just (e, rest')
  _                   -> Nothing
parseFactor s@(c:_)
  | isDigit c = let (digits, rest) = span isDigit s
                in Just (Num (read digits), rest)
parseFactor _ = Nothing
