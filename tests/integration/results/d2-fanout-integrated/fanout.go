package fanout

import "sync"

// FanOut distributes work from input channel across n workers.
func FanOut[T any, R any](
	input <-chan T,
	n int,
	fn func(T) R,
) <-chan R {
	out := make(chan R)

	var wg sync.WaitGroup
	for i := 0; i < n; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for item := range input {
				out <- fn(item)
			}
		}()
	}

	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}
