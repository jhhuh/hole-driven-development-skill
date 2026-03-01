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
	// Fresh context derived from the one stored on the struct.
	ctx, cancel := context.WithCancel(p.ctx)
	defer cancel()

	// First-error capture: thread-safe, cancels context on first error.
	var firstErr error
	var errOnce sync.Once
	setErr := func(err error) {
		if err != nil {
			errOnce.Do(func() {
				firstErr = err
				cancel()
			})
		}
	}

	// Launch producers: all write to shared channel, closed when all finish.
	prodCh := make(chan T, p.bufSize)
	var prodWg sync.WaitGroup
	for _, fn := range p.producers {
		prodWg.Add(1)
		go func(f producerFn[T]) {
			defer prodWg.Done()
			setErr(f(ctx, prodCh))
		}(fn)
	}
	go func() {
		prodWg.Wait()
		close(prodCh)
	}()
	ch := prodCh

	// Chain stages: each stage reads from ch, writes to out, then ch = out.
	for _, s := range p.stages {
		out := make(chan T, p.bufSize)
		var stageWg sync.WaitGroup
		for range s.workers {
			stageWg.Add(1)
			go func(in <-chan T, fn func(context.Context, T) (T, error)) {
				defer stageWg.Done()
				for item := range in {
					// Check if pipeline was cancelled before processing.
					if ctx.Err() != nil {
						// Drain remaining input to unblock upstream.
						for range in {
						}
						return
					}
					result, err := fn(ctx, item)
					if err != nil {
						setErr(err)
						for range in {
						}
						return
					}
					out <- result
				}
			}(ch, s.fn)
		}
		go func() {
			stageWg.Wait()
			close(out)
		}()
		ch = out
	}

	// Collect results from the final stage output.
	var results []T
	for item := range ch {
		results = append(results, item)
	}
	return results, firstErr
}
