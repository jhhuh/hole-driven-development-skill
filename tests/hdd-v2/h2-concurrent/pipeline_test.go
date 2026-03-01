package pipeline

import (
	"context"
	"errors"
	"fmt"
	"sort"
	"testing"
)

func TestBasicPipeline(t *testing.T) {
	p := NewPipeline[int](context.Background(), 10)

	// Two producers: one sends 1,2,3 and the other sends 4,5,6
	p.AddProducer(func(ctx context.Context, out chan<- int) error {
		for _, v := range []int{1, 2, 3} {
			out <- v
		}
		return nil
	})
	p.AddProducer(func(ctx context.Context, out chan<- int) error {
		for _, v := range []int{4, 5, 6} {
			out <- v
		}
		return nil
	})

	// Stage 1: double
	p.AddStage("double", 2, func(ctx context.Context, item int) (int, error) {
		return item * 2, nil
	})

	// Stage 2: add 1
	p.AddStage("add1", 2, func(ctx context.Context, item int) (int, error) {
		return item + 1, nil
	})

	results, err := p.Run()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	sort.Ints(results)
	expected := []int{3, 5, 7, 9, 11, 13}
	if len(results) != len(expected) {
		t.Fatalf("got %d results, want %d: %v", len(results), len(expected), results)
	}
	for i := range expected {
		if results[i] != expected[i] {
			t.Errorf("results[%d] = %d, want %d", i, results[i], expected[i])
		}
	}
}

func TestErrorCancelsPipeline(t *testing.T) {
	p := NewPipeline[int](context.Background(), 10)

	p.AddProducer(func(ctx context.Context, out chan<- int) error {
		for i := 0; i < 100; i++ {
			select {
			case out <- i:
			case <-ctx.Done():
				return ctx.Err()
			}
		}
		return nil
	})

	errBoom := errors.New("boom")
	p.AddStage("fail", 2, func(ctx context.Context, item int) (int, error) {
		if item == 5 {
			return 0, errBoom
		}
		return item, nil
	})

	_, err := p.Run()
	if err == nil {
		t.Fatal("expected error, got nil")
	}
	// The first error should be captured (could be errBoom or ctx.Err from producer).
	// At minimum, an error must be returned.
	t.Logf("got error (expected): %v", err)
}

func TestNoStages(t *testing.T) {
	p := NewPipeline[string](context.Background(), 5)

	p.AddProducer(func(ctx context.Context, out chan<- string) error {
		out <- "hello"
		out <- "world"
		return nil
	})

	results, err := p.Run()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	sort.Strings(results)
	if len(results) != 2 || results[0] != "hello" || results[1] != "world" {
		t.Fatalf("unexpected results: %v", results)
	}
}

func TestContextCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	p := NewPipeline[int](ctx, 10)

	p.AddProducer(func(ctx context.Context, out chan<- int) error {
		for i := 0; ; i++ {
			select {
			case out <- i:
			case <-ctx.Done():
				return ctx.Err()
			}
		}
	})

	p.AddStage("passthrough", 2, func(ctx context.Context, item int) (int, error) {
		if item >= 10 {
			cancel() // cancel from outside
		}
		return item, nil
	})

	results, err := p.Run()
	// Pipeline should terminate. We don't check exact results since
	// cancellation timing is non-deterministic.
	t.Logf("got %d results, err=%v", len(results), err)
	if err != nil && !errors.Is(err, context.Canceled) {
		t.Fatalf("unexpected error type: %v", err)
	}
}

func TestManyWorkers(t *testing.T) {
	p := NewPipeline[int](context.Background(), 20)

	p.AddProducer(func(ctx context.Context, out chan<- int) error {
		for i := 0; i < 50; i++ {
			out <- i
		}
		return nil
	})

	p.AddStage("identity", 8, func(ctx context.Context, item int) (int, error) {
		return item, nil
	})

	results, err := p.Run()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(results) != 50 {
		t.Fatalf("got %d results, want 50", len(results))
	}
	sort.Ints(results)
	for i := 0; i < 50; i++ {
		if results[i] != i {
			t.Errorf("results[%d] = %d, want %d", i, results[i], i)
		}
	}
}

func TestProducerError(t *testing.T) {
	p := NewPipeline[int](context.Background(), 5)

	errProd := fmt.Errorf("producer failed")
	p.AddProducer(func(ctx context.Context, out chan<- int) error {
		out <- 1
		return errProd
	})

	p.AddStage("double", 1, func(ctx context.Context, item int) (int, error) {
		return item * 2, nil
	})

	_, err := p.Run()
	if err == nil {
		t.Fatal("expected error from producer")
	}
	t.Logf("got error (expected): %v", err)
}
