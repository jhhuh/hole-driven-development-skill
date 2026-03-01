module Stack where

import Control.Monad.State

type Stack = [Int]

push :: Int -> State Stack ()
push x = modify (x:)

pop :: State Stack Int
pop = do
  s <- get
  let (x:xs) = s
  put xs
  return x

evalRPN :: [String] -> State Stack ()
evalRPN = mapM_ step
  where
    step "+" = do a <- pop; b <- pop; push (b + a)
    step "-" = do a <- pop; b <- pop; push (b - a)
    step "*" = do a <- pop; b <- pop; push (b * a)
    step n   = push (read n)
