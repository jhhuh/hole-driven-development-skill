{-# LANGUAGE TypeFamilies #-}
module TypeFamily where

class MyClass a where
  type family Result a :: *
  process :: a -> Result a

instance MyClass Int where
  type Result Int = String
  process = show
