package pipeline

import (
	"context"
	"sync"
)

// Pipeline processes items through multiple stages with bounded buffers.
type Pipeline[T any] struct {
	ctx       context.Context
	cancel    context.CancelFunc
	bufSize   int
	producers []func(ctx context.Context, out chan<- T) error
	stages    []stage[T]
}

type stage[T any] struct {
	name    string
	workers int
	fn      func(ctx context.Context, item T) (T, error)
}

func NewPipeline[T any](ctx context.Context, bufSize int) *Pipeline[T] {
	ctx, cancel := context.WithCancel(ctx)
	return &Pipeline[T]{
		ctx:     ctx,
		cancel:  cancel,
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
	defer p.cancel()

	var (
		firstErr error
		errOnce  sync.Once
	)
	setErr := func(err error) {
		errOnce.Do(func() {
			firstErr = err
			p.cancel()
		})
	}

	// HOLE_1: Run all producers concurrently, writing to first channel [FILLED]
	firstCh := make(chan T, p.bufSize)
	var prodWg sync.WaitGroup
	for _, prodFn := range p.producers {
		prodWg.Add(1)
		go func(fn func(ctx context.Context, out chan<- T) error) {
			defer prodWg.Done()
			if err := fn(p.ctx, firstCh); err != nil {
				setErr(err)
			}
		}(prodFn)
	}
	go func() {
		prodWg.Wait()
		close(firstCh)
	}()

	// HOLE_2: Chain stages — each reads from previous channel, writes to next [FILLED]
	in := firstCh
	for _, s := range p.stages {
		out := make(chan T, p.bufSize)
		var stageWg sync.WaitGroup
		for range s.workers {
			stageWg.Add(1)
			go func(fn func(ctx context.Context, item T) (T, error), in <-chan T, out chan<- T) {
				defer stageWg.Done()
				for {
					select {
					case item, ok := <-in:
						if !ok {
							return
						}
						result, err := fn(p.ctx, item)
						if err != nil {
							setErr(err)
							return
						}
						select {
						case out <- result:
						case <-p.ctx.Done():
							return
						}
					case <-p.ctx.Done():
						return
					}
				}
			}(s.fn, in, out)
		}
		go func() {
			stageWg.Wait()
			close(out)
		}()
		in = out
	}
	finalCh := in

	// HOLE_3: Collect results from final channel [FILLED]
	var results []T
	for item := range finalCh {
		results = append(results, item)
	}

	// HOLE_4: Wait for everything, return results and first error [FILLED]
	return results, firstErr
}
