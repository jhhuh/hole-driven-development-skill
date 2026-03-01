package fanout

import "sync"

// FanOut takes items from a single input channel and distributes
// them across n worker goroutines. Each worker applies fn and sends
// results to the output channel. Returns when input is closed and
// all workers finish.
func FanOut[T any, R any](
	input <-chan T,
	n int,
	fn func(T) R,
) <-chan R {
	out := make(chan R)

	var wg sync.WaitGroup
	wg.Add(n)

	for i := 0; i < n; i++ {
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
