module Stack where

import Control.Monad.State

type Stack = [Int]

push :: Int -> State Stack ()
push x = modify (x :)

pop :: State Stack Int
pop = do
  (x:xs) <- get
  put xs
  return x

evalRPN :: [String] -> State Stack ()
evalRPN = mapM_ step
  where
    step "+" = binOp (+)
    step "-" = binOp (-)
    step "*" = binOp (*)
    step n   = push (read n)

    binOp op = do
      b <- pop
      a <- pop
      push (a `op` b)
