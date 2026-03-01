module MySort where

-- | Sort a list using insertion sort
mySort :: Ord a => [a] -> [a]
mySort [] = []
mySort (x:xs) = insert x (mySort xs)

insert :: Ord a => a -> [a] -> [a]
insert y [] = [y]
insert y (x:xs)
  | y <= x    = y : x : xs
  | otherwise = x : insert y xs
