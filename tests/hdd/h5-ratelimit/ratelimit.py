"""
Composable, thread-safe rate limiter with multiple strategies.

Strategies:
  1. Token Bucket: steady-state rate with burst capacity
  2. Sliding Window: exact count over rolling time window
  3. Per-Client Limiting: separate limits per client ID with cleanup
  4. Global + Per-Client: compose global and per-client limits (must pass BOTH)

Requirements:
  - Thread-safe (multiple threads calling acquire() concurrently)
  - Support both blocking (wait) and non-blocking (try) modes
  - Composable: RateLimiter instances can be combined
  - Clean up stale per-client state
  - Time-based: use time.monotonic
  - Composite acquire must be atomic: can't acquire from limiter A then fail on B

Usage:
  tb = TokenBucket(rate=100, burst=20)
  sw = SlidingWindow(max_requests=1000, window_seconds=60)
  pc = PerClientLimiter(rate=10, burst=5, cleanup_interval=300)
  limiter = CompositeRateLimiter([sw, pc])

  limiter.acquire(client_id="user123")  # blocking
  if limiter.try_acquire(client_id="user123"):  # non-blocking
      handle_request()
"""

import threading
import time
from abc import ABC, abstractmethod
from collections import deque


class RateLimiter(ABC):
    @abstractmethod
    def acquire(self, client_id: str = None) -> None:
        pass

    @abstractmethod
    def try_acquire(self, client_id: str = None) -> bool:
        pass

    def _give_back(self, client_id: str = None) -> None:
        """Undo one acquire. Used by CompositeRateLimiter for atomicity."""
        raise NotImplementedError


class TokenBucket(RateLimiter):
    """Steady-state rate with burst capacity. Ignores client_id."""

    def __init__(self, rate: float, burst: int):
        self._rate = rate          # tokens per second
        self._burst = burst        # max tokens (capacity)
        self._tokens = float(burst)  # start full
        self._lock = threading.Lock()
        self._last_refill = time.monotonic()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    def try_acquire(self, client_id: str = None) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= 1:
                self._tokens -= 1
                return True
            return False

    def _give_back(self, client_id: str = None) -> None:
        with self._lock:
            self._tokens = min(self._burst, self._tokens + 1)

    def acquire(self, client_id: str = None) -> None:
        while not self.try_acquire(client_id):
            time.sleep(1.0 / self._rate)


class SlidingWindow(RateLimiter):
    """Exact count over a rolling time window. Ignores client_id."""

    def __init__(self, max_requests: int, window_seconds: float):
        self._max_requests = max_requests
        self._window = window_seconds
        self._timestamps: deque[float] = deque()
        self._lock = threading.Lock()

    def _evict_old(self, now: float):
        cutoff = now - self._window
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()

    def try_acquire(self, client_id: str = None) -> bool:
        with self._lock:
            now = time.monotonic()
            self._evict_old(now)
            if len(self._timestamps) < self._max_requests:
                self._timestamps.append(now)
                return True
            return False

    def _give_back(self, client_id: str = None) -> None:
        with self._lock:
            if self._timestamps:
                self._timestamps.pop()

    def acquire(self, client_id: str = None) -> None:
        while not self.try_acquire(client_id):
            time.sleep(self._window / self._max_requests)


class PerClientLimiter(RateLimiter):
    """Separate TokenBucket per client_id with periodic cleanup of stale entries."""

    def __init__(self, rate: float, burst: int, cleanup_interval: float = 300.0):
        self._rate = rate
        self._burst = burst
        self._cleanup_interval = cleanup_interval
        self._clients: dict[str, tuple[TokenBucket, float]] = {}  # client_id -> (bucket, last_used)
        self._lock = threading.Lock()
        self._last_cleanup = time.monotonic()

    def _get_bucket(self, client_id: str) -> TokenBucket:
        now = time.monotonic()
        if now - self._last_cleanup > self._cleanup_interval:
            self._cleanup()
            self._last_cleanup = now
        if client_id not in self._clients:
            self._clients[client_id] = (TokenBucket(self._rate, self._burst), now)
        else:
            bucket, _ = self._clients[client_id]
            self._clients[client_id] = (bucket, now)
        return self._clients[client_id][0]

    def _cleanup(self):
        now = time.monotonic()
        cutoff = now - self._cleanup_interval
        stale = [cid for cid, (_, last_used) in self._clients.items() if last_used < cutoff]
        for cid in stale:
            del self._clients[cid]

    def try_acquire(self, client_id: str = None) -> bool:
        with self._lock:
            bucket = self._get_bucket(client_id)
        return bucket.try_acquire()

    def _give_back(self, client_id: str = None) -> None:
        with self._lock:
            bucket = self._get_bucket(client_id)
        bucket._give_back()

    def acquire(self, client_id: str = None) -> None:
        with self._lock:
            bucket = self._get_bucket(client_id)
        bucket.acquire()


class CompositeRateLimiter(RateLimiter):
    """Compose multiple RateLimiters. acquire must pass ALL. Atomic: no partial acquires."""

    def __init__(self, limiters: list[RateLimiter]):
        self._limiters = list(limiters)
        self._lock = threading.Lock()

    def try_acquire(self, client_id: str = None) -> bool:
        with self._lock:
            acquired = []
            for limiter in self._limiters:
                if limiter.try_acquire(client_id):
                    acquired.append(limiter)
                else:
                    # Undo all previously acquired limiters
                    for prev in acquired:
                        prev._give_back(client_id)
                    return False
            return True

    def acquire(self, client_id: str = None) -> None:
        while not self.try_acquire(client_id):
            time.sleep(0.01)

    def _give_back(self, client_id: str = None) -> None:
        for limiter in self._limiters:
            limiter._give_back(client_id)
