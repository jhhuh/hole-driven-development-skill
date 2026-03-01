module FoldMap where

-- | Map each element to a monoid and combine the results
myFoldMap :: Monoid m => (a -> m) -> [a] -> m
myFoldMap f []     = mempty
myFoldMap f (x:xs) = f x <> myFoldMap f xs
