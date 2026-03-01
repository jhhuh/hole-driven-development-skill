package pipeline

import (
	"context"
	"sync"
)

type producerFn[T any] func(ctx context.Context, out chan<- T) error

type stage[T any] struct {
	name    string
	workers int
	fn      func(ctx context.Context, item T) (T, error)
}

// Pipeline processes items through multiple stages with bounded buffers.
type Pipeline[T any] struct {
	ctx       context.Context
	bufSize   int
	producers []producerFn[T]
	stages    []stage[T]
}

func NewPipeline[T any](ctx context.Context, bufSize int) *Pipeline[T] {
	return &Pipeline[T]{
		ctx:     ctx,
		bufSize: bufSize,
	}
}

func (p *Pipeline[T]) AddProducer(fn func(ctx context.Context, out chan<- T) error) {
	p.producers = append(p.producers, fn)
}

func (p *Pipeline[T]) AddStage(name string, workers int, fn func(ctx context.Context, item T) (T, error)) {
	p.stages = append(p.stages, stage[T]{name: name, workers: workers, fn: fn})
}

func (p *Pipeline[T]) Run() ([]T, error) {
	ctx, cancel := context.WithCancel(p.ctx)
	defer cancel()

	// errOnce captures the first error from any goroutine.
	var (
		firstErr error
		errOnce  sync.Once
	)
	setErr := func(err error) {
		errOnce.Do(func() {
			firstErr = err
			cancel()
		})
	}

	// --- Producers ---
	// All producers write to a single shared channel.
	producerCh := make(chan T, p.bufSize)
	var producerWg sync.WaitGroup
	for _, fn := range p.producers {
		producerWg.Add(1)
		go func(fn producerFn[T]) {
			defer producerWg.Done()
			if err := fn(ctx, producerCh); err != nil {
				setErr(err)
			}
		}(fn)
	}
	// Close the producer channel once all producers finish.
	go func() {
		producerWg.Wait()
		close(producerCh)
	}()

	// --- Stages ---
	// Each stage reads from the previous channel and writes to a new one.
	// Multiple workers per stage fan out from in, fan in to out.
	var in <-chan T = producerCh
	for _, s := range p.stages {
		in = runStage(ctx, s, in, p.bufSize, setErr)
	}

	// --- Collect results ---
	var results []T
	for item := range in {
		results = append(results, item)
	}

	if firstErr != nil {
		return nil, firstErr
	}
	return results, nil
}

// runStage launches workers that read from in, apply fn, and write to out.
// The returned channel is closed when all workers finish.
func runStage[T any](ctx context.Context, s stage[T], in <-chan T, bufSize int, setErr func(error)) <-chan T {
	out := make(chan T, bufSize)
	var wg sync.WaitGroup

	for i := 0; i < s.workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for item := range in {
				result, err := s.fn(ctx, item)
				if err != nil {
					setErr(err)
					// Drain the rest of in so upstream isn't blocked.
					// Other workers sharing this channel will also help drain.
					// Once ctx is cancelled, producers/prior stages will stop
					// sending, so this loop terminates.
					continue
				}
				select {
				case out <- result:
				case <-ctx.Done():
					return
				}
			}
		}()
	}

	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}
