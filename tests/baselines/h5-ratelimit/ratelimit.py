"""
Composable, thread-safe rate limiter with multiple strategies.

Strategies:
  1. Token Bucket: steady-state rate with burst capacity
  2. Sliding Window: exact count over a rolling time window
  3. Per-Client Limiting: separate limits per client ID
  4. Global + Per-Client: compose global and per-client limits

Usage:
  tb = TokenBucket(rate=100, burst=20)
  sw = SlidingWindow(max_requests=1000, window_seconds=60)
  pc = PerClientLimiter(rate=10, burst=5, cleanup_interval=300)
  limiter = CompositeRateLimiter([sw, pc])

  limiter.acquire(client_id="user123")       # blocking
  limiter.try_acquire(client_id="user123")   # non-blocking
"""

import collections
import threading
import time
from abc import ABC, abstractmethod


class RateLimiter(ABC):
    @abstractmethod
    def acquire(self, client_id: str = None) -> None:
        """Block until request is allowed."""
        pass

    @abstractmethod
    def try_acquire(self, client_id: str = None) -> bool:
        """Return True if allowed, False if rate limited. Non-blocking."""
        pass


class TokenBucket(RateLimiter):
    """Token bucket: tokens refill at `rate` per second up to `burst` capacity."""

    def __init__(self, rate: float, burst: int):
        self._rate = rate
        self._burst = burst
        self._tokens = float(burst)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)

    def _refill(self):
        """Add tokens based on elapsed time. Caller must hold self._lock."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    def _check_and_consume(self) -> bool:
        """Refill, then consume one token if available. Caller must hold self._lock."""
        self._refill()
        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return True
        return False

    def try_acquire(self, client_id: str = None) -> bool:
        with self._lock:
            return self._check_and_consume()

    def acquire(self, client_id: str = None) -> None:
        with self._cv:
            while True:
                if self._check_and_consume():
                    return
                deficit = 1.0 - self._tokens
                wait_time = deficit / self._rate
                self._cv.wait(timeout=wait_time)


class SlidingWindow(RateLimiter):
    """Sliding window: at most `max_requests` in any rolling `window_seconds` period."""

    def __init__(self, max_requests: int, window_seconds: float):
        self._max_requests = max_requests
        self._window = window_seconds
        self._timestamps = collections.deque()
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)

    def _purge(self, now: float):
        """Remove timestamps older than the window. Caller must hold self._lock."""
        cutoff = now - self._window
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()

    def _check_and_record(self) -> bool:
        """Purge old entries, record if under limit. Caller must hold self._lock."""
        now = time.monotonic()
        self._purge(now)
        if len(self._timestamps) < self._max_requests:
            self._timestamps.append(now)
            return True
        return False

    def try_acquire(self, client_id: str = None) -> bool:
        with self._lock:
            return self._check_and_record()

    def acquire(self, client_id: str = None) -> None:
        with self._cv:
            while True:
                if self._check_and_record():
                    return
                # Wait until the oldest timestamp expires out of the window.
                oldest = self._timestamps[0]
                now = time.monotonic()
                wait_time = max(0.0, (oldest + self._window) - now) + 0.001
                self._cv.wait(timeout=wait_time)


class PerClientLimiter(RateLimiter):
    """Per-client token buckets. Each client_id gets its own TokenBucket.

    Stale buckets (not used for `cleanup_interval` seconds) are periodically removed.
    """

    def __init__(self, rate: float, burst: int, cleanup_interval: float = 300.0):
        self._rate = rate
        self._burst = burst
        self._cleanup_interval = cleanup_interval
        self._buckets: dict[str, TokenBucket] = {}
        self._last_used: dict[str, float] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.monotonic()

    def _maybe_cleanup(self):
        """Remove buckets that haven't been used recently. Caller must hold self._lock."""
        now = time.monotonic()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        self._last_cleanup = now
        stale = [
            cid
            for cid, ts in self._last_used.items()
            if now - ts > self._cleanup_interval
        ]
        for cid in stale:
            del self._buckets[cid]
            del self._last_used[cid]

    def _get_bucket(self, client_id: str) -> TokenBucket:
        """Get or create the bucket for a client. Acquires self._lock internally."""
        with self._lock:
            self._maybe_cleanup()
            self._last_used[client_id] = time.monotonic()
            bucket = self._buckets.get(client_id)
            if bucket is None:
                bucket = TokenBucket(rate=self._rate, burst=self._burst)
                self._buckets[client_id] = bucket
            return bucket

    def try_acquire(self, client_id: str = None) -> bool:
        cid = client_id or "__default__"
        return self._get_bucket(cid).try_acquire()

    def acquire(self, client_id: str = None) -> None:
        cid = client_id or "__default__"
        self._get_bucket(cid).acquire()


class CompositeRateLimiter(RateLimiter):
    """Compose multiple limiters: a request must pass ALL of them.

    try_acquire is all-or-nothing for the built-in limiter types: if any
    sub-limiter would reject, none consume a token. This is achieved by
    acquiring all internal locks, checking availability, then committing
    or aborting atomically.

    For PerClientLimiter, the composite acquires both the outer dict lock
    and the inner per-client bucket lock to achieve full atomicity.

    acquire() spins on try_acquire() with a short sleep, which is correct
    because each attempt is atomic.
    """

    def __init__(self, limiters: list[RateLimiter]):
        self._limiters = list(limiters)

    def try_acquire(self, client_id: str = None) -> bool:
        # Collect all the locks we need to hold for an atomic check-then-commit.
        # For PerClientLimiter we need two locks: the dict lock and the bucket lock.
        # We sort all locks by id() to prevent deadlock from inconsistent ordering.

        lock_items = []  # (sort_key, lock) pairs
        # State we'll need during check/commit:
        buckets = {}  # maps PerClientLimiter id -> TokenBucket for that client
        flat_limiters = []  # the "leaf" limiters to check (TokenBucket or SlidingWindow)

        for lim in self._limiters:
            if isinstance(lim, TokenBucket):
                lock_items.append((id(lim._lock), lim._lock))
                flat_limiters.append(lim)
            elif isinstance(lim, SlidingWindow):
                lock_items.append((id(lim._lock), lim._lock))
                flat_limiters.append(lim)
            elif isinstance(lim, PerClientLimiter):
                # We need the dict lock to look up / create the bucket, and the
                # bucket lock to do the atomic check. But we can't know the bucket
                # lock until we hold the dict lock. So we acquire the dict lock
                # first (it's included in our sorted set), look up the bucket,
                # then acquire the bucket lock too.
                lock_items.append((id(lim._lock), lim._lock))
                # We'll resolve the bucket after acquiring locks -- see below.
            elif isinstance(lim, CompositeRateLimiter):
                # Nested composites: fall back to their try_acquire.
                # This is a simplification; full recursive lock gathering is complex.
                flat_limiters.append(lim)
            else:
                # Unknown limiter type: fall back to its own try_acquire.
                flat_limiters.append(lim)

        # Sort locks by id to prevent deadlock.
        lock_items.sort(key=lambda t: t[0])

        # Acquire all known locks.
        acquired_locks = []
        try:
            for _, lock in lock_items:
                lock.acquire()
                acquired_locks.append(lock)

            # Now that we hold all dict locks, resolve PerClientLimiter buckets
            # and acquire their locks too.
            extra_locks = []
            for lim in self._limiters:
                if isinstance(lim, PerClientLimiter):
                    cid = client_id or "__default__"
                    # Inline the bucket lookup since we already hold lim._lock.
                    lim._maybe_cleanup()
                    lim._last_used[cid] = time.monotonic()
                    bucket = lim._buckets.get(cid)
                    if bucket is None:
                        bucket = TokenBucket(rate=lim._rate, burst=lim._burst)
                        lim._buckets[cid] = bucket
                    buckets[id(lim)] = bucket
                    # Acquire the bucket's lock (if not already in our set).
                    if bucket._lock not in {lk for _, lk in lock_items}:
                        bucket._lock.acquire()
                        extra_locks.append(bucket._lock)
                        acquired_locks.append(bucket._lock)
                    flat_limiters.append(bucket)

            # Phase 1: Check all leaf limiters.
            for lim in flat_limiters:
                if isinstance(lim, TokenBucket):
                    lim._refill()
                    if lim._tokens < 1.0:
                        return False
                elif isinstance(lim, SlidingWindow):
                    lim._purge(time.monotonic())
                    if len(lim._timestamps) >= lim._max_requests:
                        return False
                else:
                    # Unknown or nested composite: call try_acquire (lossy on rollback).
                    if not lim.try_acquire(client_id=client_id):
                        return False

            # Phase 2: All checks passed -- commit.
            for lim in flat_limiters:
                if isinstance(lim, TokenBucket):
                    lim._tokens -= 1.0
                elif isinstance(lim, SlidingWindow):
                    lim._timestamps.append(time.monotonic())
                # else: already consumed via try_acquire above

            return True

        finally:
            for lock in reversed(acquired_locks):
                lock.release()

    def acquire(self, client_id: str = None) -> None:
        while not self.try_acquire(client_id=client_id):
            time.sleep(0.001)
